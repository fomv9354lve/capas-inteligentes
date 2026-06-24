# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
from __future__ import annotations

import numpy as np

from harness import BenchResult, report, time_call


TRIVIAL_NDARRAY_MAX = 1000


class LazyValue:
    __slots__ = ("value",)

    def __init__(self, value):
        self.value = value

    def is_trivial(self) -> bool:
        if isinstance(self.value, (int, float, complex)):
            return True
        return isinstance(self.value, np.ndarray) and self.value.size < TRIVIAL_NDARRAY_MAX

    def __add__(self, other):
        right = other.value if isinstance(other, LazyValue) else other
        if self.is_trivial() and (not isinstance(other, LazyValue) or other.is_trivial()):
            return LazyValue(self.value + right)
        return LazyNode("+", self, other)

    def __matmul__(self, other):
        right = other.value if isinstance(other, LazyValue) else other
        if self.is_trivial() and (not isinstance(other, LazyValue) or other.is_trivial()):
            return LazyValue(self.value @ right)
        return LazyNode("@", self, other)

    def observe(self):
        return self.value


class LazyNode:
    __slots__ = ("op", "left", "right")

    def __init__(self, op: str, left, right):
        self.op = op
        self.left = left
        self.right = right

    def observe(self):
        left = self.left.observe() if hasattr(self.left, "observe") else self.left
        right = self.right.observe() if hasattr(self.right, "observe") else self.right
        if self.op == "+":
            return left + right
        if self.op == "@":
            return left @ right
        raise ValueError(self.op)


def overhead_pct(raw_ms: float, measured_ms: float) -> float:
    return (measured_ms - raw_ms) / max(raw_ms, 1e-9) * 100


def verdict_for(overhead: float, threshold: float = 10.0) -> str:
    return "PASS" if overhead <= threshold else "FAIL"


def compare_case(name: str, raw_fn, lazy_fn, threshold: float = 10.0) -> BenchResult:
    raw = time_call(raw_fn)
    lazy = time_call(lazy_fn)
    overhead = overhead_pct(raw["ms_median"], lazy["ms_median"])
    return BenchResult(
        name,
        verdict_for(overhead, threshold),
        {
            "raw_ms": round(raw["ms_median"], 8),
            "lazy_ms": round(lazy["ms_median"], 8),
            "overhead_pct": round(overhead, 2),
            "threshold_pct": threshold,
        },
        f"raw={raw['ms_median']:.6f}ms lazy={lazy['ms_median']:.6f}ms overhead={overhead:+.1f}%",
    )


def run() -> list[BenchResult]:
    results: list[BenchResult] = []

    results.append(compare_case(
        "scalar_wrap_only",
        lambda: 1.0,
        lambda: LazyValue(1.0),
        threshold=10.0,
    ))

    a_scalar, b_scalar = LazyValue(1.0), LazyValue(2.0)
    results.append(compare_case(
        "scalar_prewrapped_add",
        lambda: 1.0 + 2.0,
        lambda: a_scalar + b_scalar,
        threshold=10.0,
    ))

    a100, b100 = np.random.default_rng(1).random(100), np.random.default_rng(2).random(100)
    la100, lb100 = LazyValue(a100), LazyValue(b100)
    results.append(compare_case(
        "vec100_prewrapped_add",
        lambda: a100 + b100,
        lambda: la100 + lb100,
        threshold=10.0,
    ))

    a32, b32 = np.random.default_rng(3).random((32, 32)), np.random.default_rng(4).random((32, 32))
    la32, lb32 = LazyValue(a32), LazyValue(b32)
    results.append(compare_case(
        "mat32_node_create_only",
        lambda: None,
        lambda: la32 @ lb32,
        threshold=0.0,
    ))

    node32 = la32 @ lb32
    results.append(compare_case(
        "mat32_observe_node",
        lambda: a32 @ b32,
        lambda: node32.observe(),
        threshold=10.0,
    ))

    a256, b256 = np.random.default_rng(5).random((256, 256)), np.random.default_rng(6).random((256, 256))
    la256, lb256 = LazyValue(a256), LazyValue(b256)
    node256 = la256 @ lb256
    results.append(compare_case(
        "mat256_observe_node",
        lambda: a256 @ b256,
        lambda: node256.observe(),
        threshold=5.0,
    ))

    return report("Benchmark 1 revised: bypass / node / observe", results)


if __name__ == "__main__":
    run()
