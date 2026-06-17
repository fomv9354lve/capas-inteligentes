from __future__ import annotations

import contextlib
import io
import json
from importlib import metadata
from pathlib import Path
from typing import Any

from rocrateValidator.validate import validate


ROOT = Path(__file__).resolve().parents[1]
CRATES = ROOT / "benchmarks" / "ro_crates"
REPORT = CRATES / "official_validation_report.json"


def run_validator(crate_dir: Path) -> dict[str, Any]:
    stream = io.StringIO()
    validator = validate(str(crate_dir.relative_to(ROOT)))
    with contextlib.redirect_stdout(stream):
        validator.validator()
    raw_result = json.loads(json.dumps(validator.get_final_result()))
    result_path = ROOT / "result.json"
    if result_path.exists():
        result_path.unlink()

    invalid = []
    warnings = []
    for check_name, values in raw_result.items():
        if values and values[0] is False:
            invalid.append({"check": check_name, "detail": values[1:]})
        for value in values:
            if isinstance(value, str) and value.startswith("WARNING"):
                warnings.append({"check": check_name, "detail": value})

    if invalid:
        status = "invalid"
    elif warnings:
        status = "valid_with_warning"
    else:
        status = "valid"

    return {
        "status": status,
        "stdout": stream.getvalue().strip(),
        "checks": raw_result,
        "invalid": invalid,
        "warnings": warnings,
    }


def main() -> int:
    crates = sorted(path for path in CRATES.glob("trace_*") if path.is_dir())
    report: dict[str, Any] = {
        "validator": {
            "package": "rocrateValidator",
            "version": metadata.version("rocrateValidator"),
            "source": "https://github.com/ResearchObject/ro-crate-validator-py",
        },
        "rocrate_library": {
            "package": "rocrate",
            "version": metadata.version("rocrate"),
        },
        "validation_scope": (
            "External RO-Crate validation using ResearchObject rocrateValidator. "
            "This is not a formal registration or external validation of the CAPAS profile."
        ),
        "crates": {},
    }

    failures = []
    for crate_dir in crates:
        result = run_validator(crate_dir)
        report["crates"][crate_dir.name] = result
        print(f"{crate_dir.name}: {result['status']}")
        for warning in result["warnings"]:
            print(f"  warning: {warning['check']}: {warning['detail']}")
        if result["status"] == "invalid":
            failures.append(crate_dir.name)

    REPORT.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(REPORT)
    if failures:
        print(f"invalid crates: {', '.join(failures)}")
        return 1
    print("external RO-Crate validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
