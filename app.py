from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.scenarios import dispatch_suggestions, flatten_suggestions

ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="GridPulse", page_icon="GP", layout="wide")


@st.cache_data
def load_artifacts():
    data = pd.read_csv(ROOT / "data/processed/net_load_hourly.csv", parse_dates=["timestamp"])
    predictions = pd.read_csv(ROOT / "outputs/models/hist_gradient_boosting_test_predictions.csv", parse_dates=["timestamp"])
    alerts = pd.read_csv(ROOT / "outputs/alerts/test_review_queue.csv", parse_dates=["timestamp"])
    importance = pd.read_csv(ROOT / "outputs/models/hist_gradient_boosting_validation_permutation_importance.csv")
    metrics = json.loads((ROOT / "outputs/models/day3_model_metrics.json").read_text(encoding="utf-8"))
    evaluation = json.loads((ROOT / "outputs/alerts/alert_evaluation.json").read_text(encoding="utf-8"))
    multihorizon = json.loads((ROOT / "outputs/models/multihorizon_metrics.json").read_text(encoding="utf-8"))
    scenario = json.loads((ROOT / "outputs/scenarios/storage_scenario_metrics.json").read_text(encoding="utf-8"))
    return data, predictions, alerts, importance, metrics, evaluation, multihorizon, scenario


def line_chart(frame: pd.DataFrame, columns: list[str], labels: list[str], title: str):
    fig, ax = plt.subplots(figsize=(12, 4))
    for column, label in zip(columns, labels):
        ax.plot(frame["timestamp"], frame[column], label=label, linewidth=1.3)
    ax.set_title(title)
    ax.set_ylabel("MW")
    ax.legend(ncol=len(columns), frameon=False)
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    st.pyplot(fig, clear_figure=True)


def risk_label(value: str) -> str:
    mapping = {"peak_load": "峰值负荷", "solar_drop": "光伏骤降", "sustained_deviation": "持续偏差"}
    return "、".join(mapping.get(item, item) for item in value.split("|"))


data, predictions, alerts, importance, metrics, evaluation, multihorizon, scenario = load_artifacts()
st.title("GridPulse 能源净负荷风险研判")
st.caption("德国公开历史数据回测原型 | 一步超前预测与直接 1--6 小时规划 | 候选运行风险，不构成调度指令或故障诊断")

with st.sidebar:
    st.header("回测范围")
    start = st.date_input("开始日期", predictions["timestamp"].min().date(), min_value=predictions["timestamp"].min().date(), max_value=predictions["timestamp"].max().date())
    end = st.date_input("结束日期", min(predictions["timestamp"].min().date() + pd.Timedelta(days=7), predictions["timestamp"].max().date()), min_value=predictions["timestamp"].min().date(), max_value=predictions["timestamp"].max().date())
    if start > end:
        st.error("结束日期不能早于开始日期。")
        st.stop()
    st.caption("所有时间均为 UTC。预测模型在时刻 t 仅使用 t-1 小时及更早的观测。")

window_predictions = predictions.loc[(predictions["timestamp"].dt.date >= start) & (predictions["timestamp"].dt.date <= end)].copy()
window_alerts = alerts.loc[(alerts["timestamp"].dt.date >= start) & (alerts["timestamp"].dt.date <= end)].copy()

overview, forecast, risks, explanation, suggestions, control = st.tabs(
    ["数据概览", "预测回测", "风险事件", "特征解释", "调度建议", "风险感知调控"]
)

with overview:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("小时记录", f"{len(data):,}")
    m2.metric("数据覆盖", "2015-01 至 2020-09")
    m3.metric("模型测试 MAE", f"{metrics['models']['hist_gradient_boosting']['test']['mae_mw']:,.0f} MW")
    m4.metric("测试人工复核队列", f"{evaluation.get('test_review_queue_rows', evaluation['test_candidate_risk_rows']):,}")
    sample = data.loc[(data["timestamp"].dt.date >= start) & (data["timestamp"].dt.date <= end)]
    line_chart(sample, ["total_load_mw", "solar_generation_mw", "wind_generation_mw", "net_load_mw"], ["总负荷", "光伏", "风电", "净负荷"], "所选时段的负荷与新能源出力")
    st.dataframe(data.describe(include="all").transpose(), use_container_width=True)

with forecast:
    if window_predictions.empty:
        st.info("该时间范围没有可展示的测试期预测。")
    else:
        line_chart(window_predictions, ["net_load_mw", "hist_gradient_boosting_prediction_mw", "hist_gradient_boosting_lower_mw", "hist_gradient_boosting_upper_mw"], ["实际净负荷", "模型预测", "预测区间下界", "预测区间上界"], "净负荷预测回测与校准区间")
        st.dataframe(window_predictions.rename(columns={"timestamp": "时间 (UTC)", "net_load_mw": "实际净负荷 (MW)", "hist_gradient_boosting_prediction_mw": "预测净负荷 (MW)", "residual_mw": "残差 (MW)"}), use_container_width=True)

with risks:
    st.caption("阈值和预测区间均来自冻结验证期；列表包含候选运行风险与仅由预测上界触发的人工复核信号，不是已确认事件。")
    if window_alerts.empty:
        st.info("所选时段没有候选风险事件。")
    else:
        display = window_alerts[["timestamp", "risk_types", "risk_evidence", "predicted_net_load_mw", "prediction_upper_mw", "risk_score", "review_priority", "residual_mw"]].copy()
        display["risk_types"] = display["risk_types"].map(risk_label)
        display = display.rename(columns={"timestamp": "时间 (UTC)", "risk_types": "风险类型", "risk_evidence": "触发证据", "predicted_net_load_mw": "预测净负荷 (MW)", "prediction_upper_mw": "预测上界 (MW)", "risk_score": "风险分数", "review_priority": "复核优先级", "residual_mw": "残差 (MW)"})
        st.dataframe(display, use_container_width=True, height=360)
        selected = st.selectbox("查看事件详情", window_alerts.index, format_func=lambda index: f"{window_alerts.loc[index, 'timestamp']} | {risk_label(window_alerts.loc[index, 'risk_types'])}")
        event = window_alerts.loc[selected]
        st.write("**触发证据：**", event["risk_evidence"])
        for item in dispatch_suggestions(event["risk_types"], event["predicted_net_load_mw"], event["residual_mw"]):
            st.write(f"**{item['action']}**：{item['reason']}")
            st.caption(item["constraint"])

with explanation:
    st.caption("验证期置换重要性：数值表示随机打乱该特征后验证 MAE 的平均恶化量；它不是因果影响。")
    top = importance.head(12).sort_values("importance_mae_mw")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(top["feature"], top["importance_mae_mw"], color="#0f766e")
    ax.set_xlabel("验证 MAE 恶化量 (MW)")
    ax.set_title("特征重要性")
    ax.grid(axis="x", alpha=0.2)
    st.pyplot(fig, clear_figure=True)
    st.dataframe(importance.rename(columns={"feature": "特征", "importance_mae_mw": "验证 MAE 恶化量 (MW)"}), use_container_width=True)

with suggestions:
    st.caption("以下为理论、规则化建议，须由具备权限的运行人员结合设备状态和安全约束审核。")
    suggestions_table = flatten_suggestions(window_alerts)
    if suggestions_table.empty:
        st.info("所选时段没有可生成的建议。")
    else:
        st.dataframe(suggestions_table, use_container_width=True, height=430)
        st.download_button("下载所选建议 CSV", suggestions_table.to_csv(index=False).encode("utf-8-sig"), "gridpulse_dispatch_suggestions.csv", "text/csv")

with control:
    st.caption("理论回测：每个小时使用直接 1--6 小时预测及验证期校准区间，滚动求解 SOC 约束削峰问题，只执行当前第一步动作。不是实际调度指令、收益或可靠性证明。")
    risk_aware = scenario["risk_aware_optimization"]["sensitivity"]
    fixed = scenario["fixed_policy"]["sensitivity"]
    comparison_rows = []
    for key in ("storage_10000mwh", "storage_20000mwh", "storage_30000mwh"):
        capacity = risk_aware[key]["capacity_mwh"] / 1000
        comparison_rows.append(
            {
                "容量 (GWh)": capacity,
                "固定储备 P95 (MW)": fixed[key]["controlled_p95_net_load_mw"],
                "风险感知 P95 (MW)": risk_aware[key]["controlled_p95_net_load_mw"],
                "P95 差值 (MW)": risk_aware[key]["controlled_p95_net_load_mw"] - fixed[key]["controlled_p95_net_load_mw"],
                "固定/风险感知等效全循环": f"{fixed[key]['equivalent_full_cycles']:.2f} / {risk_aware[key]['equivalent_full_cycles']:.2f}",
                "风险感知最低 SOC (MWh)": risk_aware[key]["min_soc_mwh"],
            }
        )
    comparison_frame = pd.DataFrame(comparison_rows)
    c1, c2, c3 = st.columns(3)
    c1.metric("规划窗口", f"{multihorizon['planning_window_hours']} 小时")
    c2.metric("30 GWh 风险感知 P95", f"{risk_aware['storage_30000mwh']['controlled_p95_net_load_mw']:,.1f} MW")
    c3.metric("30 GWh 求解最优率", f"{risk_aware['storage_30000mwh']['solver_optimal_rate_pct']:.0f}%")
    st.dataframe(comparison_frame, use_container_width=True, hide_index=True)
    st.caption("解释：固定储备规则更激进地追求单一最大点削峰；风险感知策略将预测上界与区间宽度转成动态 SOC 储备，在 20/30 GWh 情景降低 P95 且显著减少理论吞吐。该差异是目标权衡，不应解释为实际电池寿命或经济收益。")
    horizon_rows = []
    for key, item in multihorizon["models"].items():
        horizon_rows.append(
            {
                "预测时距": f"{item['horizon_hours']} 小时",
                "测试 MAE (MW)": item["test"]["mae_mw"],
                "区间覆盖率 (%)": item["prediction_interval"]["test"]["coverage_pct"],
                "区间半宽 (MW)": item["prediction_interval"]["radius_mw"],
            }
        )
    st.dataframe(pd.DataFrame(horizon_rows), use_container_width=True, hide_index=True)
