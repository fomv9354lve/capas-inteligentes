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
from router.cost_model import CLIFFORD_GATES, magic_estimate  # noqa: E402


ROTATION_GATES = {"RX", "RY", "RZ", "U", "U1", "U2", "U3"}
EXPLICIT_T_GATES = {"T", "TDG"}
TRACTABLE_T = 16
MAYBE_T = 32


@dataclass(frozen=True)
class DecompositionRow:
    name: str
    family: str
    n_qubits: int
    epsilon: float
    n_gates: int
    explicit_t_count: int
    arbitrary_rotation_count: int
    estimated_t_per_rotation: int
    estimated_total_t_count: int
    zone: str
    low_alpha_log10_rank_proxy: float
    high_alpha_log10_rank_proxy: float


def estimated_t_per_rotation(epsilon: float) -> int:
    """Ross-Selinger-style triage estimate for arbitrary z-rotations.

    Typical T-count scales as about 3 * log2(1/epsilon) plus lower-order terms.
    This is a feasibility estimate, not exact synthesis.
    """
    if epsilon <= 0 or epsilon >= 1:
        raise ValueError("epsilon must be in (0, 1)")
    return math.ceil(3 * math.log2(1 / epsilon))


def classify_t(t_count: int) -> str:
    if t_count == 0:
        return "clifford"
    if t_count <= TRACTABLE_T:
        return "tractable_low_magic"
    if t_count <= MAYBE_T:
        return "maybe_boundary"
    return "too_high_for_low_magic_backend"


def log10_rank_proxy(t_count: int, alpha: float) -> float:
    return alpha * t_count * math.log10(2)


def count_arbitrary_rotations(ops: list[tuple[str, tuple[int, ...]]]) -> int:
    return sum(1 for gate, _ in ops if str(gate).upper() in ROTATION_GATES)


def rows_for_epsilon(epsilon: float) -> list[DecompositionRow]:
    t_per_rotation = estimated_t_per_rotation(epsilon)
    rows: list[DecompositionRow] = []
    for case in build_corpus():
        magic = magic_estimate(case.ops)
        rotations = count_arbitrary_rotations(case.ops)
        explicit_t = sum(1 for gate, _ in case.ops if str(gate).upper() in EXPLICIT_T_GATES)
        estimated_total_t = explicit_t + rotations * t_per_rotation
        rows.append(
            DecompositionRow(
                name=case.name,
                family=case.family,
                n_qubits=case.n_qubits,
                epsilon=epsilon,
                n_gates=magic.n_gates,
                explicit_t_count=explicit_t,
                arbitrary_rotation_count=rotations,
                estimated_t_per_rotation=t_per_rotation,
                estimated_total_t_count=estimated_total_t,
                zone=classify_t(estimated_total_t),
                low_alpha_log10_rank_proxy=round(log10_rank_proxy(estimated_total_t, 0.23), 3),
                high_alpha_log10_rank_proxy=round(log10_rank_proxy(estimated_total_t, 0.5), 3),
            )
        )
    return rows


def summarize(rows: list[DecompositionRow]) -> dict:
    zone_counts = defaultdict(int)
    family = defaultdict(lambda: defaultdict(int))
    large_n_low = []
    large_n_too_high = []
    for row in rows:
        zone_counts[row.zone] += 1
        family[row.family][row.zone] += 1
        if row.n_qubits >= 30 and row.zone in {"tractable_low_magic", "maybe_boundary"}:
            large_n_low.append(row.name)
        if row.n_qubits >= 30 and row.zone == "too_high_for_low_magic_backend":
            large_n_too_high.append(row.name)

    return {
        "epsilon": rows[0].epsilon if rows else None,
        "estimated_t_per_rotation": rows[0].estimated_t_per_rotation if rows else None,
        "zone_counts": dict(sorted(zone_counts.items())),
        "family_zone_counts": {k: dict(sorted(v.items())) for k, v in sorted(family.items())},
        "large_n_low_or_boundary_count": len(large_n_low),
        "large_n_too_high_count": len(large_n_too_high),
        "large_n_low_or_boundary_cases": large_n_low,
        "large_n_too_high_cases": large_n_too_high,
    }


def main() -> int:
    epsilons = [1e-3, 1e-6, 1e-9]
    all_rows = []
    summaries = []
    for epsilon in epsilons:
        rows = rows_for_epsilon(epsilon)
        all_rows.extend(rows)
        summaries.append(summarize(rows))

    output = {
        "model": {
            "rotation_t_count_estimate": "ceil(3 * log2(1 / epsilon))",
            "source": "Ross-Selinger typical asymptotic T-count for ancilla-free Clifford+T z-rotation approximation",
            "note": "triage estimate, not exact synthesis",
        },
        "summaries": summaries,
        "rows": [asdict(row) for row in all_rows],
    }
    path = ROOT / "benchmarks" / "decompose_magic_estimate_results.json"
    path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(output["model"], indent=2, sort_keys=True))
    for summary in summaries:
        print("\n" + json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
