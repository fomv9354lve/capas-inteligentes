from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bench_claim_frequency import build_corpus  # noqa: E402
from router.cost_model import magic_estimate  # noqa: E402


TRACTABLE_T = 16
MAYBE_T = 32


@dataclass(frozen=True)
class MagicScalingRow:
    name: str
    family: str
    n_qubits: int
    n_gates: int
    t_count: int
    non_clifford_count: int
    zone: str
    stabilizer_rank_cost_low_alpha: float
    stabilizer_rank_cost_high_alpha: float


def zone_for(t_count: int, non_clifford_count: int) -> str:
    if non_clifford_count == 0:
        return "clifford"
    if t_count == non_clifford_count:
        if t_count <= TRACTABLE_T:
            return "low_magic_clifford_t_candidate"
        if t_count <= MAYBE_T:
            return "maybe_clifford_t_boundary"
        return "high_magic_clifford_t"
    if t_count == 0:
        return "arbitrary_rotation_or_non_t_magic"
    if t_count <= TRACTABLE_T:
        return "mixed_low_t_with_other_magic"
    return "high_magic"


def stabilizer_cost_proxy(t_count: int, alpha: float) -> float:
    """Simple order-of-growth proxy: 2 ** (alpha * T).

    This is not a runtime model. It is a triage number for deciding whether
    the low-magic regime is even plausible before building a backend.
    """
    return 2 ** (alpha * t_count)


def make_rows() -> list[MagicScalingRow]:
    rows = []
    for case in build_corpus():
        magic = magic_estimate(case.ops)
        rows.append(
            MagicScalingRow(
                name=case.name,
                family=case.family,
                n_qubits=case.n_qubits,
                n_gates=magic.n_gates,
                t_count=magic.t_count,
                non_clifford_count=magic.non_clifford_count,
                zone=zone_for(magic.t_count, magic.non_clifford_count),
                stabilizer_rank_cost_low_alpha=round(stabilizer_cost_proxy(magic.t_count, 0.23), 3),
                stabilizer_rank_cost_high_alpha=round(stabilizer_cost_proxy(magic.t_count, 0.5), 3),
            )
        )
    return rows


def summarize(rows: list[MagicScalingRow]) -> dict:
    by_family = defaultdict(list)
    for row in rows:
        by_family[row.family].append(row)

    families = {}
    for family, fam_rows in sorted(by_family.items()):
        counts = defaultdict(int)
        for row in fam_rows:
            counts[row.zone] += 1
        t_values = [r.t_count for r in fam_rows]
        families[family] = {
            "n_cases": len(fam_rows),
            "n_qubits": sorted({r.n_qubits for r in fam_rows}),
            "t_min": min(t_values),
            "t_max": max(t_values),
            "t_values": sorted(t_values),
            "zones": dict(sorted(counts.items())),
        }

    total = len(rows)
    zone_counts = defaultdict(int)
    for row in rows:
        zone_counts[row.zone] += 1

    interesting = [
        row
        for row in rows
        if row.zone == "low_magic_clifford_t_candidate" and row.n_qubits >= 30
    ]
    high_n_high_magic = [
        row
        for row in rows
        if row.zone in {"high_magic", "high_magic_clifford_t", "arbitrary_rotation_or_non_t_magic"} and row.n_qubits >= 30
    ]

    return {
        "total_cases": total,
        "zone_counts": dict(sorted(zone_counts.items())),
        "low_magic_large_n_cases": len(interesting),
        "high_magic_large_n_cases": len(high_n_high_magic),
        "family_summary": families,
        "interpretation": {
            "tractable_t_cutoff": TRACTABLE_T,
            "maybe_t_cutoff": MAYBE_T,
            "large_n_cutoff": 30,
            "claim_signal": (
                "present"
                if interesting
                else "absent"
            ),
        },
    }


def main() -> int:
    rows = make_rows()
    summary = summarize(rows)
    output = {
        "summary": summary,
        "rows": [asdict(row) for row in rows],
    }
    path = ROOT / "benchmarks" / "magic_scaling_results.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))
    print("\nLarge-n low-magic candidates:")
    for row in rows:
        if row.zone == "low_magic_clifford_t_candidate" and row.n_qubits >= 30:
            print(
                f"  {row.name:<24} family={row.family:<22} "
                f"n={row.n_qubits:<3} T={row.t_count:<3} "
                f"proxy[0.23]={row.stabilizer_rank_cost_low_alpha:<8} "
                f"proxy[0.5]={row.stabilizer_rank_cost_high_alpha}"
            )

    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
