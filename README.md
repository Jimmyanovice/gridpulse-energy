# GridPulse · 参赛材料与可复现原型

面向新能源波动的净负荷预测与风险感知储能规划。使用真实公开的德国电力系统历史数据，将数据质量检查、净负荷预测、预测区间、风险复核和受约束储能规划连接成可运行、可审计的原型。

本仓库发布 2026-10-13 整理的参赛材料快照。完整材料在 [提交目录](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/)；目录内 310 个文件与本地干净提交包逐字节一致，不包含旧项目的 Git 历史。

## 从这里开始

- [提交说明与待办](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/00_提交说明.md)
- [赛题、解答与可视化的通俗导读](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/05_复现与合规/project-walkthrough-zh.md)
- [技术报告 PDF](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/01_技术报告/GridPulse-技术报告.pdf) · [报告源稿](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/01_技术报告/GridPulse-技术报告源稿.md)
- [答辩 PDF](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/02_答辩材料/GridPulse-答辩材料.pdf) · [可编辑 PPTX](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/02_答辩材料/GridPulse-答辩材料.pptx)
- [赛题要求与实现对照](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/05_复现与合规/competition-alignment.md)

## 材料目录

| 目录 | 内容 |
|---|---|
| `01_技术报告` | 最终 PDF 与 Markdown 源稿 |
| `02_答辩材料` | 最终 PDF 与可编辑 PPTX |
| `03_源代码` | 应用、算法、测试、依赖、标准化数据、模型、实验轨迹与图表 |
| `04_实验结果` | 实验工件索引，链接到源码内的唯一数据副本 |
| `05_复现与合规` | 方法、数据来源、原创性说明、数学证书范围及验证回执 |
| `06_平台上传文件` | 按提交命名规则准备的两份 PDF |

## 运行仪表盘

需要 Python 3.11 或更高版本。克隆仓库后，在仓库根目录执行：

```powershell
cd TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/03_源代码
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

数据、模型和结果快照已随仓库提供，无需下载原始数据或重新训练即可查看仪表盘。完整实验复现见 [复现说明](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/05_复现与合规/reproducibility.md)。重新训练请使用独立副本，避免改变冻结证据的哈希。

在仓库根目录验证提交快照：

```powershell
python TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/03_源代码/scripts/validate_submission_package.py TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse
```

应用与数值实验不需要 Node.js。PPT 构建脚本依赖本地提供的私有创作工具，普通环境可直接编辑已经提供的 PPTX；详情见 [PPT 工具说明](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/03_源代码/scripts/ppt/README.md)。

## 证据与结论范围

2021/2022 年锁定复验均复现全年最高净负荷削减 1,250 MW，相对原动态策略的平均日峰值改善保持为正。P95 优势未稳定复现，储能吞吐与损耗增加；季度不利结果和预测区间覆盖下降均保留在报告与应用中。

[有限实例最优性证书](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/05_复现与合规/global-optimality.md)只证明指定物理模型、给定历史轨迹和目标下的结果。作品是历史回测与理论规划原型，尚无真实电网部署、实际收益或所有未来情景最优的证据。

## 清理与提交状态

本快照保留报告、答辩、代码、模型、标准化数据、图表、冻结协议、验证轨迹与校验清单。已排除缓存、虚拟环境、`node_modules`、参考仓库、原始大数据、旧版报告/PPT、旧压缩包及本地工具状态。

`MANIFEST.json` 与 `SHA256SUMS.txt` 覆盖提交目录中的材料；仓库根目录 README、LICENSE、Git 配置文件不在该提交清单范围内。Git 属性关闭文本换行转换，以保护冻结文件的字节和哈希。

正式比赛提交仍需替换 `TEAM-ID-TO-RENAME` 为官方团队编号、完成最终人工匿名审核，并按官方平台要求上传。MP4 演示视频暂未包含。GitHub 发布不替代赛事指定的提交渠道。

## 许可与来源

原创代码采用 [MIT License](LICENSE)。公开数据及其他第三方材料适用各自条款，来源与归属见 [第三方说明](TEAM-ID-TO-RENAME-AIC-AI能源-GridPulse/03_源代码/THIRD_PARTY_NOTICES.md)。
