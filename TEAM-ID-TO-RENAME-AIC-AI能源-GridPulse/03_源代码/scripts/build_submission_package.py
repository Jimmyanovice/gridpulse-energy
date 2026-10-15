from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import re
from datetime import date
from pathlib import Path

from validate_submission_package import validate


ROOT = Path(__file__).resolve().parents[1]
SUBMISSION_ROOT = ROOT / "submission"
DEFAULT_TEAM_ID = "TEAM-ID-TO-RENAME"

SOURCE_FILES = (
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "requirements.txt",
    "pytest.ini",
    "app.py",
    "package.json",
    "CONTRIBUTING.md",
    "SECURITY.md",
)
DOCS = (
    "architecture.md",
    "anonymous-submission.md",
    "competition-alignment.md",
    "data-dictionary.md",
    "data-source-decision.md",
    "demo-script.md",
    "originality-and-provenance.md",
    "reproducibility.md",
    "risk-aware-control.md",
    "peak-response.md",
    "independent-validation.md",
    "global-optimality.md",
    "controller-development.md",
    "later-year-validation.md",
    "release-review.md",
    "project-walkthrough-zh.md",
    "submission-checklist.md",
)
RESULTS = (
    "outputs/metrics/data-quality-report.json",
    "outputs/metrics/seasonal_naive_metrics.json",
    "outputs/models/day3_model_metrics.json",
    "outputs/models/multihorizon_metrics.json",
    "outputs/models/rolling_backtest_metrics.json",
    "outputs/models/reference_baseline_metrics.json",
    "outputs/models/hist_gradient_boosting_validation_permutation_importance.csv",
    "outputs/scenarios/reserve_ablation_metrics.json",
    "outputs/scenarios/daily_energy_balance_metrics.json",
    "outputs/scenarios/daily_fixed_open_timeseries.csv",
    "outputs/scenarios/daily_dynamic_open_timeseries.csv",
    "outputs/scenarios/daily_fixed_balanced_timeseries.csv",
    "outputs/scenarios/daily_dynamic_balanced_timeseries.csv",
    "outputs/scenarios/peak_response_metrics.json",
    "outputs/scenarios/peak_validation_fixed_upper_timeseries.csv",
    "outputs/scenarios/peak_validation_dynamic_upper_timeseries.csv",
    "outputs/scenarios/peak_validation_dynamic_release_only_timeseries.csv",
    "outputs/scenarios/peak_validation_dynamic_point_only_timeseries.csv",
    "outputs/scenarios/peak_validation_dynamic_peak_response_timeseries.csv",
    "outputs/scenarios/peak_validation_fixed_peak_response_timeseries.csv",
    "outputs/scenarios/peak_test_dynamic_release_only_timeseries.csv",
    "outputs/scenarios/peak_test_dynamic_point_only_timeseries.csv",
    "outputs/scenarios/peak_test_dynamic_peak_response_timeseries.csv",
    "outputs/scenarios/peak_test_fixed_peak_response_timeseries.csv",
    "outputs/models/hist_gradient_boosting_test_predictions.csv",
    "outputs/models/direct_horizon_test_predictions.csv",
    "outputs/models/hist_gradient_boosting.joblib",
    "outputs/models/direct_horizon_1h.joblib",
    "outputs/models/direct_horizon_2h.joblib",
    "outputs/models/direct_horizon_3h.joblib",
    "outputs/models/direct_horizon_4h.joblib",
    "outputs/models/direct_horizon_5h.joblib",
    "outputs/models/direct_horizon_6h.joblib",
    "outputs/predictions/seasonal_naive_test.csv",
    "outputs/alerts/alert_evaluation.json",
    "outputs/alerts/test_candidate_risks.csv",
    "outputs/alerts/test_review_queue.csv",
    "outputs/scenarios/storage_scenario_metrics.json",
    "outputs/scenarios/storage_10000mwh_direct_fixed_reserve_timeseries.csv",
    "outputs/scenarios/storage_10000mwh_risk_aware_timeseries.csv",
    "outputs/scenarios/storage_20000mwh_direct_fixed_reserve_timeseries.csv",
    "outputs/scenarios/storage_20000mwh_risk_aware_timeseries.csv",
    "outputs/scenarios/storage_30000mwh_direct_fixed_reserve_timeseries.csv",
    "outputs/scenarios/storage_30000mwh_risk_aware_timeseries.csv",
    "data/processed/net_load_hourly.csv",
    "data/processed/independent_de_2021_hourly.csv",
    "outputs/validation/independent_2021_protocol.json",
    "outputs/validation/independent_2021_metrics.json",
    "outputs/validation/independent_2021_data_quality.json",
    "outputs/validation/independent_2021_robustness.json",
    "outputs/validation/independent_2021_predictions.csv",
    "outputs/validation/independent_2021_fixed_upper_timeseries.csv",
    "outputs/validation/independent_2021_dynamic_upper_timeseries.csv",
    "outputs/validation/independent_2021_dynamic_release_only_timeseries.csv",
    "outputs/validation/independent_2021_dynamic_point_only_timeseries.csv",
    "outputs/validation/independent_2021_dynamic_peak_response_timeseries.csv",
    "outputs/validation/independent_2021_fixed_peak_response_timeseries.csv",
    "outputs/optimality/certificates.json",
    "outputs/optimality/independent_2021_oracle.csv",
    "outputs/optimality/exploratory_test_oracle.csv",
)

# Validation lineage is byte-sensitive. Preserve protocol, calibration and
# evidence snapshots exactly; reserializing JSON would invalidate SHA-256.
FROZEN_JSON = {"outputs/scenarios/reserve_ablation_metrics.json",
    "outputs/scenarios/storage_scenario_metrics.json", "outputs/scenarios/peak_response_metrics.json"}


def copy_file(relative: str, target: Path) -> None:
    source = ROOT / relative
    if not source.is_file():
        raise FileNotFoundError(f"Required submission input is missing: {relative}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if relative in FROZEN_JSON or relative.startswith("outputs/validation/"):
        if source.suffix == ".json" and re.search(r'"[A-Za-z]:[\\/]', source.read_text(encoding="utf-8")):
            raise ValueError("Frozen evidence contains an absolute path; review without rewriting its lineage.")
        shutil.copy2(source, target)
    elif source.suffix == ".json":
        value = json.loads(source.read_text(encoding="utf-8"))
        target.write_text(json.dumps(portable_json(value), ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        shutil.copy2(source, target)


def portable_json(value):
    if isinstance(value, dict):
        return {key: portable_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [portable_json(item) for item in value]
    if isinstance(value, str) and re.match(r"^[A-Za-z]:[\\/]", value):
        normalized = value.replace("\\", "/")
        root = ROOT.as_posix() + "/"
        return normalized[len(root):] if normalized.lower().startswith(root.lower()) else normalized.rsplit("/", 1)[-1]
    return value


def copy_tree(relative: str, target: Path, suffixes: set[str] | None = None) -> None:
    source = ROOT / relative
    if not source.is_dir():
        raise FileNotFoundError(f"Required source directory is missing: {relative}")
    for item in source.rglob("*"):
        if item.is_file() and (suffixes is None or item.suffix in suffixes):
            destination = target / item.relative_to(source)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(package: Path) -> None:
    entries = []
    for path in sorted(item for item in package.rglob("*") if item.is_file()):
        relative = path.relative_to(package).as_posix()
        if relative in {"MANIFEST.json", "SHA256SUMS.txt"}:
            continue
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)})
    manifest = {
        "schemaVersion": "gridpulse-submission-package.v1",
        "generatedOn": date.today().isoformat(),
        "contents": "Anonymous GridPulse competition package, excluding the required MP4 demonstration video.",
        "files": entries,
    }
    (package / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (package / "SHA256SUMS.txt").write_text(
        "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries), encoding="utf-8"
    )


def write_submission_note(package: Path, team_id: str) -> None:
    text = f"""# GridPulse 提交说明

## 项目信息

- 申报组别：AIC AI+能源科技创新组
- 作品名称：GridPulse：面向新能源波动的净负荷预测与风险感知储能规划
- 当前文件夹名称：`{package.name}`
- 打包日期：{date.today().isoformat()}

## 材料目录

| 目录 | 内容 |
|---|---|
| `01_技术报告` | 技术报告 PDF 与可追溯 Markdown 源稿 |
| `02_答辩材料` | 答辩 PDF 与可编辑 PPTX |
| `03_源代码` | 可运行原型、复现脚本、测试与依赖清单 |
| `04_实验结果` | 质量、预测、风险、储能情景的关键输出与图表 |
| `05_复现与合规` | 数据来源、复现、匿名、原创性、赛题对齐材料 |
| `06_平台上传文件` | 按“团队编号-赛题名称-作品名称-材料名称”预命名的两份 PDF；编号仍需替换 |

## 数据与复现

首次阅读可先打开 [赛题与作品通俗导读](05_复现与合规/project-walkthrough-zh.md)，其中逐项解释官方要求、六个应用标签页、九张静态图和十五页答辩材料。

原开发实验使用 Open Power System Data（OPSD）Time Series 2020-10-06；后续冻结时间留出与锁定复验使用 Energy-Charts.info 德国 2021/2022 数据（CC BY 4.0）。数据 DOI、字段映射、归属和下载方式见 `05_复现与合规/data-source-decision.md`、`05_复现与合规/independent-validation.md`、`05_复现与合规/later-year-validation.md` 与 `03_源代码/THIRD_PARTY_NOTICES.md`。本目录不附第三方原始大 CSV/JSON；标准化快照、冻结协议、预测、控制轨迹与模型工件已附。模型和校准文件受冻结哈希约束，重训练后不能再沿用原预登记。完整路径见 `05_复现与合规/reproducibility.md`。

新增有限实例最优性证明见 `05_复现与合规/global-optimality.md`，精确有理数和 LP 原始-对偶证书位于 `03_源代码/outputs/optimality`。2021 年现有策略达到固定物理模型的全年最高点下界，但不代表吞吐、P95 或所有未来在线最优。新版报告和答辩已同步数学证明与循环代价开发复核，运行压力、区间和新能源关联分析见 `05_复现与合规/controller-development.md`；开发候选未通过准入，原冻结策略保留。

## 提交边界

- 本包已排除 `.git`、`.github`、`CITATION.cff`、本地缓存、参考仓库、原始大数据和旧版答辩材料。
- 本包不含 MP4 演示视频；请在正式提交前录制真实的 3--5 分钟视频并按赛事要求加入提交渠道。
- `TEAM-ID-TO-RENAME` 是占位符。请将文件夹开头替换为赛事分配的真实团队编号：当前值为 `{team_id}`。
- 官网附件指定百度网盘：仍需由参赛队上传其他材料，设置永久有效分享、提供提取码，并完成最终人工匿名检查。不得以本说明替代该人工核验。
- `06_平台上传文件` 的 PDF 可分别用于技术报告和答辩栏目。正式上传前将占位编号替换为真实团队编号，并核对平台的赛题名称；内部源码路径保留，以便复现。其他材料按官方命名规则整理。

## 校验

`MANIFEST.json` 和 `SHA256SUMS.txt` 列出本包内文件及 SHA-256 校验值。生成后可运行：

```powershell
python 03_源代码/scripts/validate_submission_package.py .
```

## 解压后直接运行

在本目录打开 PowerShell，执行：

```powershell
cd 03_源代码
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

所需标准化数据、预测、特征重要性和结果均位于 `03_源代码/data` 与 `03_源代码/outputs`，无需重新训练即可查看仪表盘。完整重训练按 `03_源代码/docs/reproducibility.md` 执行。`04_实验结果` 保存实验索引，避免重复存放模型。
"""
    (package / "00_提交说明.md").write_text(text, encoding="utf-8")


def build(team_id: str, replace: bool) -> Path:
    safe_team_id = team_id.strip()
    if not safe_team_id or any(character in safe_team_id for character in "\\/:"):
        raise ValueError("team ID must be non-empty and must not contain path separators or ':'.")
    SUBMISSION_ROOT.mkdir(exist_ok=True)
    package = (SUBMISSION_ROOT / f"{safe_team_id}-AIC-AI能源-GridPulse").resolve()
    if package.parent != SUBMISSION_ROOT.resolve():
        raise ValueError("Submission target escaped the submission directory.")
    if package.exists():
        if not replace:
            raise FileExistsError(f"Submission package already exists: {package}. Use --replace to rebuild it.")
        shutil.rmtree(package)
    package.mkdir()

    write_submission_note(package, safe_team_id)
    copy_file("outputs/report/gridpulse-technical-report-v0.1.pdf", package / "01_技术报告/GridPulse-技术报告.pdf")
    copy_file("docs/technical-report-draft.md", package / "01_技术报告/GridPulse-技术报告源稿.md")
    report_source = package / "01_技术报告/GridPulse-技术报告源稿.md"
    report_source.write_text(report_source.read_text(encoding="utf-8").replace(
        "](outputs/figures/", "](../03_源代码/outputs/figures/"
    ), encoding="utf-8")
    copy_file("outputs/presentation/gridpulse-defense-v9.pdf", package / "02_答辩材料/GridPulse-答辩材料.pdf")
    copy_file("outputs/presentation/gridpulse-defense-v9.pptx", package / "02_答辩材料/GridPulse-答辩材料.pptx")
    for relative, label in (
        ("outputs/report/gridpulse-technical-report-v0.1.pdf", "技术报告"),
        ("outputs/presentation/gridpulse-defense-v9.pdf", "答辩材料"),
    ):
        copy_file(relative, package / "06_平台上传文件" / f"{package.name}-{label}.pdf")

    for relative in SOURCE_FILES:
        copy_file(relative, package / "03_源代码" / relative)
    copy_tree("src", package / "03_源代码/src", {".py"})
    copy_tree("scripts", package / "03_源代码/scripts", {".py", ".mjs", ".md", ".ps1"})
    copy_tree("tests", package / "03_源代码/tests", {".py"})
    copy_tree("docs", package / "03_源代码/docs", {".md"})
    packaged_readme = package / "03_源代码/README.md"
    readme = packaged_readme.read_text(encoding="utf-8")
    readme = re.sub(r"## Citation\n.*?(?=## License)", "", readme, flags=re.S)
    packaged_readme.write_text(readme, encoding="utf-8")
    for relative in (
        "outputs/report/gridpulse-technical-report-v0.1.pdf",
        "outputs/presentation/gridpulse-defense-v9.pptx",
        "outputs/presentation/gridpulse-defense-v9.pdf",
    ):
        copy_file(relative, package / "03_源代码" / relative)
    copy_tree("outputs/figures", package / "03_源代码/outputs/figures", {".png"})

    for relative in RESULTS:
        copy_file(relative, package / "03_源代码" / relative)
    copy_tree("outputs/development",package / "03_源代码/outputs/development",{".json",".csv",".txt"})
    if (ROOT / "outputs/experiments").is_dir():
        copy_tree("outputs/experiments", package / "03_源代码/outputs/experiments", {".json", ".csv"})
    later_results = tuple(source.relative_to(ROOT).as_posix()
                          for source in sorted((ROOT/"outputs/validation").glob("independent_2022_*")))
    for relative in later_results:
        source = ROOT / relative
        copy_file(source.relative_to(ROOT).as_posix(), package/"03_源代码"/source.relative_to(ROOT))
    copy_file("data/processed/independent_de_2022_hourly.csv", package/"03_源代码/data/processed/independent_de_2022_hourly.csv")
    index = package / "04_实验结果/实验索引.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index_results = RESULTS + ("data/processed/independent_de_2022_hourly.csv",) + later_results
    index.write_text("# 实验工件索引\n\n" + "\n".join(f"- [{relative}](../03_源代码/{relative})" for relative in index_results) + "\n\n图表位于 `../03_源代码/outputs/figures`。新增开发协议、完整控制/压力轨迹、区间/新能源诊断和干净环境回执位于 `../03_源代码/outputs/development`，解读见 `../05_复现与合规/controller-development.md`。2022 年锁定复验解读见 [later-year-validation.md](../05_复现与合规/later-year-validation.md)。\n", encoding="utf-8")

    for document in DOCS:
        copy_file(f"docs/{document}", package / "05_复现与合规" / document)
        if document == "project-walkthrough-zh.md":
            walkthrough = package / "05_复现与合规" / document
            walkthrough.write_text(walkthrough.read_text(encoding="utf-8").replace(
                "](../outputs/", "](../03_源代码/outputs/"), encoding="utf-8")
    for receipt in (
        ".codex-finalizer/gridpulse-final-preflight.json",
        ".codex-finalizer/gridpulse-anonymous-preflight.json",
        ".codex-finalizer/gridpulse-defense-v9.validation.json",
    ):
        copy_file(receipt, package / "05_复现与合规/验证回执" / Path(receipt).name)

    write_manifest(package)
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the compact, anonymous GridPulse competition package.")
    parser.add_argument("--team-id", default=DEFAULT_TEAM_ID, help="Official team ID. The default is an explicit placeholder.")
    parser.add_argument("--replace", action="store_true", help="Replace an existing package with the same team ID under submission/.")
    args = parser.parse_args()
    package = build(args.team_id, args.replace)
    report = validate(package)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Submission package: {package}")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
