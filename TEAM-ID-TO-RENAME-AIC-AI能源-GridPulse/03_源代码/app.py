from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
import pandas as pd
import streamlit as st

from src.scenarios import dispatch_suggestions, flatten_suggestions
from src.artifacts import ArtifactError, inspect_runtime, validate_frame

ROOT = Path(__file__).resolve().parent
for family in ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "WenQuanYi Zen Hei"):
    if family in {font.name for font in font_manager.fontManager.ttflist}:
        plt.rcParams["font.sans-serif"] = [family]
        plt.rcParams["axes.unicode_minus"] = False
        break

st.set_page_config(page_title="GridPulse", page_icon="GP", layout="wide")

REQUIRED_ARTIFACTS = (
    "data/processed/net_load_hourly.csv",
    "outputs/models/hist_gradient_boosting_test_predictions.csv",
    "outputs/alerts/test_review_queue.csv",
    "outputs/models/hist_gradient_boosting_validation_permutation_importance.csv",
    "outputs/models/day3_model_metrics.json", "outputs/alerts/alert_evaluation.json",
    "outputs/models/multihorizon_metrics.json", "outputs/scenarios/storage_scenario_metrics.json",
    "outputs/models/reference_baseline_metrics.json", "outputs/scenarios/reserve_ablation_metrics.json",
    "outputs/scenarios/daily_energy_balance_metrics.json", "outputs/scenarios/peak_response_metrics.json",
    "outputs/validation/independent_2021_metrics.json", "outputs/optimality/certificates.json",
    "outputs/development/controller_metrics.json", "outputs/development/operating_stress_metrics.json",
    "outputs/development/renewable_alignment_metrics.json", "outputs/development/interval_audit_metrics.json",
    "outputs/validation/independent_2022_metrics.json",
)
missing = [name for name in REQUIRED_ARTIFACTS if not (ROOT/name).is_file()]
if missing:
    st.error("演示所需数据或结果工件缺失。请使用完整解压的项目包，或按 docs/reproducibility.md 生成结果。")
    st.code("\n".join(missing),language="text")
    st.stop()

try:
    artifact_fingerprint = inspect_runtime(ROOT, REQUIRED_ARTIFACTS)
except ArtifactError as exc:
    st.error(str(exc))
    st.stop()


@st.cache_data
def load_artifacts(fingerprint):
    data = pd.read_csv(ROOT / "data/processed/net_load_hourly.csv", parse_dates=["timestamp"])
    predictions = pd.read_csv(ROOT / "outputs/models/hist_gradient_boosting_test_predictions.csv", parse_dates=["timestamp"])
    alerts = pd.read_csv(ROOT / "outputs/alerts/test_review_queue.csv", parse_dates=["timestamp"])
    alerts["risk_types"] = alerts["risk_types"].fillna("interval_peak_watch")
    importance = pd.read_csv(ROOT / "outputs/models/hist_gradient_boosting_validation_permutation_importance.csv")
    for frame, name in ((data, "net_load_hourly.csv"), (predictions, "hist_gradient_boosting_test_predictions.csv"),
                        (alerts, "test_review_queue.csv"), (importance, "hist_gradient_boosting_validation_permutation_importance.csv")):
        validate_frame(frame, name)
    metrics = json.loads((ROOT / "outputs/models/day3_model_metrics.json").read_text(encoding="utf-8"))
    evaluation = json.loads((ROOT / "outputs/alerts/alert_evaluation.json").read_text(encoding="utf-8"))
    multihorizon = json.loads((ROOT / "outputs/models/multihorizon_metrics.json").read_text(encoding="utf-8"))
    scenario = json.loads((ROOT / "outputs/scenarios/storage_scenario_metrics.json").read_text(encoding="utf-8"))
    baselines = json.loads((ROOT / "outputs/models/reference_baseline_metrics.json").read_text(encoding="utf-8"))
    reserve_ablation = json.loads((ROOT / "outputs/scenarios/reserve_ablation_metrics.json").read_text(encoding="utf-8"))
    daily_balance = json.loads((ROOT / "outputs/scenarios/daily_energy_balance_metrics.json").read_text(encoding="utf-8"))
    peak_response = json.loads((ROOT / "outputs/scenarios/peak_response_metrics.json").read_text(encoding="utf-8"))
    independent = json.loads((ROOT / "outputs/validation/independent_2021_metrics.json").read_text(encoding="utf-8"))
    return data, predictions, alerts, importance, metrics, evaluation, multihorizon, scenario, baselines, reserve_ablation, daily_balance, peak_response, independent


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
    if pd.isna(value) or not value:
        value = "interval_peak_watch"
    mapping = {"peak_load": "峰值负荷", "solar_drop": "光伏骤降", "sustained_deviation": "持续偏差", "interval_peak_watch": "预测区间峰值预警"}
    return "、".join(mapping.get(item, item) for item in value.split("|"))


try:
    data, predictions, alerts, importance, metrics, evaluation, multihorizon, scenario, baselines, reserve_ablation, daily_balance, peak_response, independent = load_artifacts(artifact_fingerprint)
except ArtifactError as exc:
    st.error(str(exc))
    st.stop()
except (OSError, ValueError, KeyError, TypeError) as exc:
    st.error("数据或结果文件结构异常。请使用完整项目包，或按 docs/reproducibility.md 重新生成结果。")
    st.stop()
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
    st.dataframe(data.describe(include="all").transpose(), width="stretch")

with forecast:
    st.caption(f"以下指标使用相同的 {baselines['test_rows']:,} 个冻结测试时间点，覆盖整个测试期，不随侧栏筛选改变。")
    names = {"persistence_1h": "上一小时持平", "seasonal_24h": "24 小时季节参考", "seasonal_168h": "168 小时季节参考", "hist_gradient_boosting": "梯度提升"}
    st.dataframe(pd.DataFrame([{"模型": names[key], "MAE (MW)": item["mae_mw"], "RMSE (MW)": item["rmse_mw"]} for key, item in baselines["metrics"].items()]), width="stretch", hide_index=True)
    if window_predictions.empty:
        st.info("该时间范围没有可展示的测试期预测。")
    else:
        line_chart(window_predictions, ["net_load_mw", "hist_gradient_boosting_prediction_mw", "hist_gradient_boosting_lower_mw", "hist_gradient_boosting_upper_mw"], ["实际净负荷", "模型预测", "预测区间下界", "预测区间上界"], "净负荷预测回测与校准区间")
        st.dataframe(window_predictions.rename(columns={"timestamp": "时间 (UTC)", "net_load_mw": "实际净负荷 (MW)", "hist_gradient_boosting_prediction_mw": "预测净负荷 (MW)", "residual_mw": "残差 (MW)"}), width="stretch")

with risks:
    st.caption("阈值和预测区间均来自冻结验证期；列表包含候选运行风险与仅由预测上界触发的人工复核信号，不是已确认事件。")
    if window_alerts.empty:
        st.info("所选时段没有候选风险事件。")
    else:
        display = window_alerts[["timestamp", "risk_types", "risk_evidence", "predicted_net_load_mw", "prediction_upper_mw", "risk_score", "review_priority", "residual_mw"]].copy()
        display["risk_types"] = display["risk_types"].map(risk_label)
        display = display.rename(columns={"timestamp": "时间 (UTC)", "risk_types": "风险类型", "risk_evidence": "触发证据", "predicted_net_load_mw": "预测净负荷 (MW)", "prediction_upper_mw": "预测上界 (MW)", "risk_score": "风险分数", "review_priority": "复核优先级", "residual_mw": "残差 (MW)"})
        st.dataframe(display, width="stretch", height=360)
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
    st.dataframe(importance.rename(columns={"feature": "特征", "importance_mae_mw": "验证 MAE 恶化量 (MW)"}), width="stretch")

with suggestions:
    st.caption("以下为理论、规则化建议，须由具备权限的运行人员结合设备状态和安全约束审核。")
    suggestions_table = flatten_suggestions(window_alerts)
    if suggestions_table.empty:
        st.info("所选时段没有可生成的建议。")
    else:
        st.dataframe(suggestions_table, width="stretch", height=430)
        st.download_button("下载所选建议 CSV", suggestions_table.to_csv(index=False).encode("utf-8-sig"), "gridpulse_dispatch_suggestions.csv", "text/csv")

with control:
    st.caption("理论回测：每个小时使用直接 1--6 小时预测及验证期校准区间，滚动求解 SOC 约束削峰问题，只执行当前第一步动作。不是实际调度指令、收益或可靠性证明。")
    risk_aware = scenario["risk_aware_optimization"]["sensitivity"]
    fixed = scenario["direct_fixed_reserve_baseline"]["sensitivity"]
    comparison_rows = []
    for key in ("storage_10000mwh", "storage_20000mwh", "storage_30000mwh"):
        capacity = risk_aware[key]["capacity_mwh"] / 1000
        comparison_rows.append(
            {
                "容量 (GWh)": capacity,
                "固定 30% 储备 P95 (MW)": fixed[key]["controlled_p95_net_load_mw"],
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
    st.dataframe(comparison_frame, width="stretch", hide_index=True)
    st.caption("原版公平消融：两种策略共享预测和优化约束，仅储备规则不同。原版区间半宽按时距固定，最大半宽使不确定性项始终饱和，储备变化主要来自峰值严重度。上述指标覆盖整个测试期。")
    st.subheader("补充实验：储备分量与功率敏感性")
    experiment_names = {"fixed_30pct": "固定 30%", "severity_only": "仅峰值严重度", "uncertainty_only": "仅区间宽度", "combined": "组合储备", "combined_half_power": "组合，放电 625 MW", "combined_double_charge_power": "组合，充电 2500 MW"}
    st.dataframe(pd.DataFrame([{"策略": experiment_names[key], "P95 (MW)": item["controlled_p95_net_load_mw"], "吞吐 (MWh)": item["throughput_mwh"], "初始 SOC (MWh)": item["initial_soc_mwh"], "期末 SOC (MWh)": item["final_soc_mwh"], "储备目标未达小时": item["reserve_target_shortfall_hours"]} for key, item in reserve_ablation["experiments"].items()]), width="stretch", hide_index=True)
    st.caption("补充实验使用验证期按小时校准的区间和独立尺度，属于原版测试结果公开后的探索性分析。储备下限取目标与当前 SOC 的较小值，属于软目标；期末 SOC 未约束为初始值，不能据此推断长期收益。所有策略均未降低全期最高净负荷。")
    st.subheader("原版每日能量恢复：削峰收益与补电代价")
    daily_names = {"fixed_open": "固定，未恢复", "dynamic_open": "动态，未恢复", "fixed_balanced": "固定，每日恢复", "dynamic_balanced": "动态，每日恢复"}
    st.dataframe(pd.DataFrame([
        {"策略": daily_names[key], "P95 (MW)": item["controlled_p95_mw"],
         "最高净负荷 (MW)": item["controlled_peak_mw"], "吞吐 (MWh)": item["throughput_mwh"],
         "转换损耗 (MWh)": item["conversion_loss_mwh"],
         "净消耗初始能量 (MWh)": item["net_initial_energy_consumed_mwh"],
         "最大日末 SOC 偏差 (MWh)": item["max_abs_terminal_error_mwh"],
         "储备目标未达小时": item["reserve_target_shortfall_hours"]}
        for key, item in daily_balance["experiments"].items()
    ]), width="stretch", hide_index=True)
    sample_daily = daily_balance["experiments"]["fixed_balanced"]
    delta = daily_balance["comparisons"]["balanced"]
    st.write(f"每日恢复对照：动态相对固定 P95 差值 {delta['dynamic_minus_fixed_p95_mw']:.2f} MW，吞吐差值 {delta['dynamic_minus_fixed_throughput_mwh']:,.2f} MWh。动态策略最高点未降低，固定策略最高点更低，不能称为全面更优。")
    st.caption(f"以上固定统计使用 {sample_daily['days']} 个完整 UTC 日、{sample_daily['rows']:,} 个小时，不随侧栏改变；排除 {len(sample_daily['omitted_partial_days'])} 个首尾不完整日。每个独立日初始 SOC 15,000 MWh，共同硬下限 4,500 MWh。每日恢复模式另将 SOC 上限设为 15,000 MWh，并允许任意小时补电，已计入增加的净负荷和转换损耗。未恢复模式每天重置初始电量，仅作实验对照。模式之间同时改变补电权限与 SOC 上限，不能只归因于日末等式；动态储备仍为软目标。本实验属于探索性分析。")
    balanced_traces = []
    for key, label in (("fixed_balanced", "固定储备 SOC"), ("dynamic_balanced", "动态储备 SOC")):
        trace = pd.read_csv(ROOT / daily_balance["experiments"][key]["timeseries"], parse_dates=["timestamp"])
        trace = trace.loc[(trace.timestamp.dt.date >= start) & (trace.timestamp.dt.date <= end)]
        balanced_traces.append((trace, label))
    if balanced_traces[0][0].empty:
        st.info("所选时段没有完整 UTC 日的储能轨迹。")
    else:
        fig, ax = plt.subplots(figsize=(12, 4))
        for trace, label in balanced_traces:
            ax.plot(trace.timestamp, trace.storage_soc_mwh, label=label, linewidth=1.2)
        ax.axhline(4500, color="#b45309", linestyle="--", label="共同硬下限")
        ax.axhline(15000, color="#50625e", linestyle=":", label="每日初末电量")
        ax.set_ylabel("SOC (MWh)")
        ax.set_title("所选完整日：储能电量与每日恢复")
        ax.legend(ncol=4, frameon=False)
        ax.grid(alpha=.2)
        fig.autofmt_xdate()
        st.pyplot(fig, clear_figure=True)
    st.subheader("极端峰值响应：储备释放与规划目标消融")
    peak_names = {"fixed_upper": "原固定，上界目标", "dynamic_upper": "原动态，上界目标",
                  "dynamic_release_only": "动态，仅释放软储备", "dynamic_point_only": "动态，仅点预测目标",
                  "dynamic_peak_response": "动态，点目标与释放", "fixed_peak_response": "固定，点目标与释放"}
    st.caption(f"窗口点预测达到验证期一小时预测的 99% 分位（{peak_response['calibration']['release_threshold_mw']:,.2f} MW）时，允许释放软储备至共同硬下限。点目标用于定位峰值；预测区间继续决定储备和放电触发。每日恢复与所有功率约束均计入。")
    for period_key, period_label in (("validation", "验证期内部诊断"), ("test", "测试期探索性复核")):
        st.write(period_label)
        st.dataframe(pd.DataFrame([
            {"策略": peak_names[key], "最高净负荷 (MW)": item["controlled_peak_mw"],
             "全期最高峰削减 (MW)": item["max_reduction_mw"], "P95 (MW)": item["controlled_p95_mw"],
             "吞吐 (MWh)": item["throughput_mwh"], "转换损耗 (MWh)": item["conversion_loss_mwh"],
             "高负荷前20小时平均削减 (MW)": item["top20_mean_reduction_mw"],
             "硬下限违规小时": item["hard_soc_violation_hours"],
             "最大日末误差 (MWh)": item["max_abs_terminal_error_mwh"]}
            for key, item in peak_response["periods"][period_key]["experiments"].items()
        ]), width="stretch", hide_index=True)
    peak_case = peak_response["periods"]["test"]["experiments"]["dynamic_peak_response"]["peak_event"]
    st.write(f"原始最高峰发生于 {peak_case['timestamp']}：实际净负荷 {peak_case['net_load_mw']:,.2f} MW，新动态策略放电 {peak_case['discharge_mw']:,.2f} MW、充电 {peak_case['charge_mw']:,.2f} MW。全期最高点可能转移，以上表中全期指标为准。")
    st.caption("这些统计覆盖各自完整日，不随侧栏日期改变。设计发生在旧测试峰值已知后；验证期也参与阈值和区间校准，所以均不能称为独立确认。释放的储备是软目标，点目标也不保留原版上界最小最大目标的解释。真实备用义务、网络、价格和退化仍需另行验证。")
    case_day = pd.Timestamp(peak_case["timestamp"]).date()
    peak_plot = []
    for key, label in (("dynamic_upper", "原动态受控净负荷"), ("dynamic_peak_response", "新动态受控净负荷"), ("fixed_peak_response", "新固定受控净负荷")):
        item = peak_response["periods"]["test"]["experiments"][key]
        trace = pd.read_csv(ROOT / item["timeseries"], parse_dates=["timestamp"])
        trace = trace.loc[trace.timestamp.dt.date.eq(case_day)]
        peak_plot.append((trace, label))
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(peak_plot[0][0].timestamp, peak_plot[0][0].net_load_mw, label="实际净负荷", color="#17302a", linewidth=1.5)
    for trace, label in peak_plot:
        ax.plot(trace.timestamp, trace.controlled_net_load_mw, label=label, linewidth=1.2)
    ax.set_ylabel("MW")
    ax.set_title("测试期原始最高峰所在日：削峰与补电负荷")
    ax.legend(ncol=2, frameon=False)
    ax.grid(alpha=.2)
    fig.autofmt_xdate()
    st.pyplot(fig, clear_figure=True)
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
    st.dataframe(pd.DataFrame(horizon_rows), width="stretch", hide_index=True)
    st.subheader("2021 年冻结时间留出：削峰复现与失败边界")
    st.caption("德国同国后续年份，Energy-Charts.info CC BY 4.0。下载全年数据前已固定协议、模型与阈值，未重训或重新校准。以下使用完整 365 日、8,760 小时，不随侧栏日期改变。")
    st.dataframe(pd.DataFrame([
        {"策略": peak_names[key], "最高净负荷 (MW)": item["controlled_peak_mw"], "P95 (MW)": item["controlled_p95_mw"],
         "吞吐 (MWh)": item["throughput_mwh"], "损耗 (MWh)": item["conversion_loss_mwh"],
         "软目标未达小时": item["reserve_target_shortfall_hours"], "硬下限违规小时": item["hard_soc_violation_hours"],
         "最大日末误差 (MWh)": item["max_abs_terminal_error_mwh"]}
        for key,item in independent["experiments"].items()
    ]), width="stretch", hide_index=True)
    primary = independent["comparisons"]["dynamic_peak_response_versus_dynamic_upper"]
    interval = primary["uncertainty"]["mean_daily_peak_reduction_mw"]
    st.write(f"新动态相对原动态全年最高点降低 {primary['full_period_peak_reduction_mw']:,.2f} MW；平均日最高点降低 {interval['estimate']:.2f} MW，7 天配对区块 95% 区间 [{interval['lower_95']:.2f}, {interval['upper_95']:.2f}] MW。")
    st.warning(f"全年 P95 变化为 {-primary['p95_reduction_mw']:+.2f} MW，P95 优势未复现；Q3 最高点变差。削峰伴随更高吞吐和损耗，新固定组合达到相同最高点，不能宣称新动态全面更优。")
    quarterly_rows = []
    for quarter in ("1","2","3","4"):
        old,new = (independent["quarters"][key][quarter] for key in ("dynamic_upper","dynamic_peak_response"))
        quarterly_rows.append({"季度": "Q"+quarter,"完整日":new["days"],"原动态最高点 (MW)":old["controlled_peak_mw"],
            "新动态最高点 (MW)":new["controlled_peak_mw"],"最高点削减，旧减新 (MW)":old["controlled_peak_mw"]-new["controlled_peak_mw"],
            "P95 削减，旧减新 (MW)":old["controlled_p95_mw"]-new["controlled_p95_mw"]})
    st.dataframe(pd.DataFrame(quarterly_rows),width="stretch",hide_index=True)
    st.caption("分位数不能按季度线性平均。重采样区间仅反映当前观测日及冻结预测下的变动，不推断未见极值。源时间戳表示区间开始，发布发生在最新观测小时结束；额外发布延迟、数据版本、网络、价格和退化仍待核验。完整协议和区块敏感性见 docs/independent-validation.md。")
    st.subheader("2022 年锁定复验：年度差异与循环代价")
    later = json.loads((ROOT/"outputs/validation/independent_2022_metrics.json").read_text(encoding="utf-8"))
    st.caption(f"下载前再次锁定原六组策略、模型与阈值。共享 {later['shared_days']} 日，遗漏 {len(later['omitted_days'])} 日；未将开发候选带入新年度选型。")
    st.dataframe(pd.DataFrame([
        {"策略": peak_names[key], "最高净负荷 (MW)": item["controlled_peak_mw"], "P95 (MW)": item["controlled_p95_mw"],
         "吞吐 (MWh)": item["throughput_mwh"], "损耗 (MWh)": item["conversion_loss_mwh"]}
        for key, item in later["experiments"].items()
    ]), width="stretch", hide_index=True)
    result = later["comparisons"]["dynamic_peak_response_versus_dynamic_upper"]
    daily_ci = result["uncertainty"]["mean_daily_peak_reduction_mw"]
    p95_ci = result["uncertainty"]["p95_reduction_mw"]
    st.write(f"相对原动态：全年最高点削减 {result['full_period_peak_reduction_mw']:,.2f} MW，平均日削峰 {daily_ci['estimate']:.2f} MW，95% 区间 [{daily_ci['lower_95']:.2f}, {daily_ci['upper_95']:.2f}]。")
    st.write(f"全年 P95 削减 {result['p95_reduction_mw']:.2f} MW，95% 区间 [{p95_ci['lower_95']:.2f}, {p95_ci['upper_95']:.2f}]；吞吐增加 {result['throughput_increase_mwh']:,.2f} MWh。")
    st.dataframe(pd.DataFrame([
        {"季度": q, "最高点削减，旧减新 (MW)": later["quarters"]["dynamic_upper"][q]["controlled_peak_mw"]-later["quarters"]["dynamic_peak_response"][q]["controlled_peak_mw"],
         "P95 削减，旧减新 (MW)": later["quarters"]["dynamic_upper"][q]["controlled_p95_mw"]-later["quarters"]["dynamic_peak_response"][q]["controlled_p95_mw"]}
        for q in later["quarters"]["dynamic_upper"]
    ]), width="stretch", hide_index=True)
    st.caption(f"全年 P95 点估计改善，但区间覆盖零，四个季度各自的 P95 均变差；年度分位数不能按季度平均。一小时预测 MAE {later['forecast_metrics']['1']['mae_mw']:.2f} MW，冻结区间覆盖率 {later['forecast_metrics']['1']['interval_coverage_pct']:.2f}%。完整方法见 docs/later-year-validation.md。")
    st.subheader("有限实例最优性：物理下界与离线差距")
    optimality = json.loads((ROOT / "outputs/optimality/certificates.json").read_text(encoding="utf-8"))
    st.dataframe(pd.DataFrame([
        {"实例": "2021 年" if name == "independent_2021" else "旧探索性测试",
         "物理最优最高点 (MW)":case["offline_benchmark"]["period_optimum_peak_mw"],
         "现有新动态最高点差距 (MW)":case["controller_peak_gap_mw"],
         "最优最高点下离线最低吞吐 (MWh)":case["offline_benchmark"]["minimum_throughput_at_optimum_peak_mwh"],
         "离线最低吞吐解 P95 (MW)":case["offline_benchmark"]["oracle_p95_mw"],
         "精确有理数证书通过":case["exact_rational_certificate"]["passed"]}
        for name,case in optimality["cases"].items()
    ]),width="stretch",hide_index=True)
    st.write("任意可行调度最高点 ≥ 原最高负荷 − 最大放电功率。2021 年为 70,449.90 − 1,250 = 69,199.90 MW，现有新策略达到此下界。")
    st.caption("证书针对固定物理模型与有限数据；离线基准预知全部真实负荷，仅依次优化全年最高点和吞吐。它不承担预测门槛或软储备规则，不能据此宣称在线收益、P95 最优、动态策略独有优势或未来全局最优。完整证明与验算见 docs/global-optimality.md；冻结模型与策略未修改。")
    with st.expander("开发复核：循环代价、运行压力与新能源关联"):
        development = json.loads((ROOT/"outputs/development/controller_metrics.json").read_text(encoding="utf-8"))
        period = st.selectbox("开发复核时段",list(development["periods"]),format_func=lambda x:{"validation":"原验证期","known_test":"已知旧测试期","known_2021":"已知 2021 年"}[x])
        st.dataframe(pd.DataFrame([
            {"配置":name,"最高点 (MW)":v["controlled_peak_mw"],"P95 (MW)":v["controlled_p95_mw"],
             "吞吐 (MWh)":v["throughput_mwh"],"损耗 (MWh)":v["conversion_loss_mwh"]}
            for name,v in development["periods"][period]["experiments"].items()
        ]),width="stretch",hide_index=True)
        st.write("验证期筛选结果：保留原冻结控制器。候选两阶段规划虽减少部分循环，但均未满足最高点最多变差 1 MW 的预设准入条件。")
        st.caption("候选配置使用窗口最优峰值加 0/100/250/500 MW 容许差，再最小化吞吐。窗口容许差不等于全年实际峰值保证，全部为已知数据上的开发复核。")
        stress = json.loads((ROOT/"outputs/development/operating_stress_metrics.json").read_text(encoding="utf-8"))
        date = st.selectbox("运行压力复核周",list(stress["episodes"]))
        st.dataframe(pd.DataFrame([
            {"情景":scenario,"配置":policy,"最高点 (MW)":e["controlled_peak_mw"],
             "吞吐 (MWh)":e["throughput_mwh"],"约束核验通过":e["physical_audit_passed"]}
            for scenario,item in stress["episodes"][date].items() for policy,e in item["experiments"].items() if e["status"] == "solved"
        ]),width="stretch",hide_index=True)
        st.caption("四个固定季度周。传递滞后测试延迟既有预测发布，跨日测试只在每个七日周内连续运行并恢复周末 SOC。通过物理约束不代表预测延迟时效果不变或现场可靠。")
        energy = json.loads((ROOT/"outputs/development/renewable_alignment_metrics.json").read_text(encoding="utf-8"))
        e = energy["periods"][period]["frozen_reference"]
        st.write(f"原策略在新能源占比不低于 {energy['high_renewable_share_threshold']:.2%} 的时段完成 {e['charge_in_high_renewable_hours_pct']:.2f}% 的充电；绝对爬坡 P95 从 {e['baseline_abs_ramp_p95_mw_per_hour']:.2f} 变为 {e['controlled_abs_ramp_p95_mw_per_hour']:.2f} MW/h。")
        st.caption("这是充电时段与实际新能源出力的事后关联，不证明充电来源或减少弃风弃光。")
        bands = json.loads((ROOT/"outputs/development/interval_audit_metrics.json").read_text(encoding="utf-8"))
        st.dataframe(pd.DataFrame(bands["groups"]),width="stretch",hide_index=True)
        st.caption("滚动区间仅使用发布时已观测的历史残差，以覆盖率、区间宽度和区间评分共同评价；尚未反馈到控制器，也未做新的独立验证。")
