from __future__ import annotations

import pandas as pd


def dispatch_suggestions(risk_types: str, predicted_net_load_mw: float, residual_mw: float) -> list[dict[str, str]]:
    """Return auditable suggestions; these are not control commands."""
    suggestions: list[dict[str, str]] = []
    active = set(filter(None, risk_types.split("|")))
    if "peak_load" in active:
        suggestions.append(
            {
                "action": "评估削峰资源预备状态",
                "reason": f"预测净负荷为 {predicted_net_load_mw:,.0f} MW，达到峰值风险阈值。",
                "constraint": "需在获得设备容量、荷电状态、用户负荷可调性和调度授权后执行。",
            }
        )
    if "solar_drop" in active:
        suggestions.append(
            {
                "action": "复核短时备用与储能响应窗口",
                "reason": "光伏出力出现快速下降，净负荷爬坡压力可能增大。",
                "constraint": "该回测信号使用实际观测光伏值；实际应用须替换为可用的预测或实时量测。",
            }
        )
    if "sustained_deviation" in active:
        direction = "高于" if residual_mw >= 0 else "低于"
        suggestions.append(
            {
                "action": "核验数据质量与运行状态",
                "reason": f"实际净负荷连续{direction}模型预期，残差为 {residual_mw:,.0f} MW。",
                "constraint": "候选偏差不等同于设备故障；需结合运行日志和人工复核。",
            }
        )
    return suggestions


def flatten_suggestions(alerts: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in alerts.itertuples(index=False):
        for suggestion in dispatch_suggestions(row.risk_types, row.predicted_net_load_mw, row.residual_mw):
            rows.append(
                {
                    "时间 (UTC)": row.timestamp,
                    "风险类型": row.risk_types,
                    "建议动作": suggestion["action"],
                    "依据": suggestion["reason"],
                    "适用约束": suggestion["constraint"],
                }
            )
    return pd.DataFrame(rows)


def simulate_storage_dispatch(
    frame: pd.DataFrame,
    peak_threshold_mw: float,
    capacity_mwh: float,
    max_power_mw: float = 2500.0,
    charge_power_mw: float = 1250.0,
    efficiency: float = 0.92,
    charge_threshold_mw: float | None = None,
    emergency_threshold_mw: float | None = None,
    reserve_fraction: float = 0.30,
    energy_smoothing_hours: float | None = None,
) -> tuple[pd.DataFrame, dict[str, float]]:
    """Run a reserve-aware, theoretical battery peak-shaving scenario at hourly resolution."""
    result = frame.copy().sort_values("timestamp").reset_index(drop=True)
    low_charge_threshold = float(
        result["predicted_net_load_mw"].quantile(0.25) if charge_threshold_mw is None else charge_threshold_mw
    )
    emergency_threshold = float(
        peak_threshold_mw if emergency_threshold_mw is None else emergency_threshold_mw
    )
    if not 0 <= reserve_fraction < 1:
        raise ValueError("reserve_fraction must be in [0, 1).")
    reserve_mwh = capacity_mwh * reserve_fraction
    effective_max_power_mw = min(
        max_power_mw,
        capacity_mwh / energy_smoothing_hours if energy_smoothing_hours else max_power_mw,
    )
    soc_mwh = capacity_mwh * 0.5
    dispatches = []
    controlled = []
    soc_values = []
    for row in result.itertuples(index=False):
        dispatch_mw = 0.0
        if row.predicted_net_load_mw >= peak_threshold_mw:
            requested = min(effective_max_power_mw, max(0.0, row.predicted_net_load_mw - peak_threshold_mw))
            available_mwh = soc_mwh if row.predicted_net_load_mw >= emergency_threshold else max(0.0, soc_mwh - reserve_mwh)
            dispatch_mw = min(requested, available_mwh * efficiency)
            soc_mwh -= dispatch_mw / efficiency
        elif row.predicted_net_load_mw <= low_charge_threshold:
            charge = min(charge_power_mw, (capacity_mwh - soc_mwh) / efficiency)
            dispatch_mw = -charge
            soc_mwh += charge * efficiency
        dispatches.append(dispatch_mw)
        controlled.append(row.net_load_mw - dispatch_mw)
        soc_values.append(soc_mwh)
    result["storage_dispatch_mw"] = dispatches
    result["storage_soc_mwh"] = soc_values
    result["controlled_net_load_mw"] = controlled
    triggered = result["predicted_net_load_mw"] >= peak_threshold_mw
    triggered_baseline = result.loc[triggered, "net_load_mw"]
    triggered_controlled = result.loc[triggered, "controlled_net_load_mw"]
    metrics = {
        "capacity_mwh": capacity_mwh,
        "max_discharge_power_mw": max_power_mw,
        "effective_discharge_power_mw": effective_max_power_mw,
        "energy_smoothing_hours": energy_smoothing_hours,
        "charge_power_mw": charge_power_mw,
        "round_trip_efficiency_proxy": efficiency**2,
        "reserve_fraction": reserve_fraction,
        "reserve_mwh": reserve_mwh,
        "baseline_max_net_load_mw": float(result["net_load_mw"].max()),
        "controlled_max_net_load_mw": float(result["controlled_net_load_mw"].max()),
        "theoretical_max_reduction_mw": float(result["net_load_mw"].max() - result["controlled_net_load_mw"].max()),
        "forecast_trigger_hours": int(triggered.sum()),
        "forecast_trigger_window_baseline_max_mw": float(triggered_baseline.max()),
        "forecast_trigger_window_controlled_max_mw": float(triggered_controlled.max()),
        "forecast_trigger_window_max_reduction_mw": float(triggered_baseline.max() - triggered_controlled.max()),
        "baseline_p95_net_load_mw": float(result["net_load_mw"].quantile(0.95)),
        "controlled_p95_net_load_mw": float(result["controlled_net_load_mw"].quantile(0.95)),
        "discharge_hours": int((result["storage_dispatch_mw"] > 0).sum()),
        "charge_hours": int((result["storage_dispatch_mw"] < 0).sum()),
        "min_soc_mwh": float(result["storage_soc_mwh"].min()),
        "max_soc_mwh": float(result["storage_soc_mwh"].max()),
        "forecast_peak_threshold_mw": peak_threshold_mw,
        "forecast_emergency_threshold_mw": emergency_threshold,
        "low_charge_forecast_threshold_mw": low_charge_threshold,
    }
    return result, metrics
