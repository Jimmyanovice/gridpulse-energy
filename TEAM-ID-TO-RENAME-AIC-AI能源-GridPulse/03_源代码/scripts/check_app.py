from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path


def check(root: Path) -> dict:
    sys.path.insert(0, str(root.resolve()))
    from streamlit.testing.v1 import AppTest

    warnings.filterwarnings("error", message="Glyph .* missing from font")
    app = AppTest.from_file(str(root / "app.py"), default_timeout=45).run()
    errors = [item.message for item in app.exception]
    if not errors:
        app.date_input[1].set_value(app.date_input[1].max).run()
        errors.extend(item.message for item in app.exception)
    if not errors:
        app.date_input[0].set_value(app.date_input[0].max).run()
        errors.extend(item.message for item in app.exception)
    if not errors:
        # A terminal partial day must explain the absent daily trace, not fail.
        if not any("所选时段没有完整 UTC 日" in item.value for item in app.info):
            errors.append("Missing incomplete-day explanation for the terminal date.")
    if not errors:
        next(x for x in app.selectbox if x.label == "开发复核时段").set_value("known_2021").run()
        errors.extend(item.message for item in app.exception)
    if not errors:
        next(x for x in app.selectbox if x.label == "运行压力复核周").set_value("2021-07-08").run()
        errors.extend(item.message for item in app.exception)
    if not errors:
        app.date_input[1].set_value(app.date_input[1].min).run()
        errors.extend(item.message for item in app.exception)
        if not any("结束日期不能早于开始日期" in item.value for item in app.error):
            errors.append("Invalid date range did not explain the error.")
    return {"passed": not errors, "checks": ["startup", "full_test_period", "last_test_day", "incomplete_daily_trace_explanation", "Chinese_plot_fonts", "development_period_selection", "stress_week_selection", "invalid_date_range"], "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    report = check(args.root.resolve())
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
