# 技术报告章节索引

完整报告源稿见 [technical-report-draft.md](technical-report-draft.md)，PDF 位于 `outputs/report/gridpulse-technical-report-v0.1.pdf`。

| 章节 | 内容 | 配套证据 |
|---|---|---|
| 摘要 | 场景、预测与规划方法、主要结果及适用范围 | 冻结预测、储能对照与年度复验 |
| 1. 项目背景与意义 | 新能源波动、净负荷定义、应用对象和研究目标 | `competition-alignment.md`、`data-source-decision.md` |
| 2. 技术方案与实现 | 数据质量、因果特征、一步与直接 1–6 小时预测、候选风险、滚动规划和七页仪表盘 | `architecture.md`、`data-dictionary.md`、`risk-aware-control.md` |
| 3. 实验与分析 | 预测基线、特征消融、规则压力测试、同信息储备对照、每日恢复、极端响应、2021/2022 复验及有限实例证书 | `day3-model-results.md`、`peak-response.md`、`independent-validation.md`、`later-year-validation.md`、`global-optimality.md` |
| 4. 创新与应用价值 | 预测到规划的工程集成、风险证据链、机制对照与方案评估 | `INNOVATION_BRIEF.md`、`controller-development.md` |
| 5. 结论与局限 | 削峰结果、P95 与循环取舍、数据泛化和现场应用条件 | 完整季度、吞吐、损耗与区间覆盖结果 |
| 参考资料与附录 | 数据、算法与软件来源，依赖和复现路径 | `THIRD_PARTY_NOTICES.md`、`originality-and-provenance.md`、`reproducibility.md` |

报告区分冻结结果、已知测试期上的探索性实验和下载前锁定的后续年份复验。历史仿真结果不等同于设备运行或经济收益，候选风险不等同于确认故障。
