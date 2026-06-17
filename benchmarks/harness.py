from __future__ import annotations

import gc
import json
import os
import time
from dataclasses import asdict, dataclass, field
from statistics import median
from typing import Any, Callable

import psutil


@dataclass
class BenchResult:
    case: str
    verdict: str
    metric: dict[str, Any] = field(default_factory=dict)
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def line(self) -> str:
        return f"[{self.verdict:<4}] {self.case:<34} {self.note}"


def time_call(fn: Callable[[], Any], repeats: int = 11, warmup: int = 3) -> dict[str, float]:
    for _ in range(warmup):
        fn()
    samples = []
    for _ in range(repeats):
        gc.disable()
        t0 = time.perf_counter()
        fn()
        t1 = time.perf_counter()
        gc.enable()
        samples.append((t1 - t0) * 1e3)
    samples.sort()
    return {
        "ms_median": median(samples),
        "ms_min": samples[0],
        "ms_max": samples[-1],
        "repeats": repeats,
    }


def current_rss_mb() -> float:
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def report(title: str, results: list[BenchResult]) -> list[BenchResult]:
    print(f"\n=== {title} ===")
    for result in results:
        print("  " + result.line())
    n_pass = sum(r.verdict == "PASS" for r in results)
    n_fail = sum(r.verdict == "FAIL" for r in results)
    n_warn = sum(r.verdict == "WARN" for r in results)
    print(f"  ---- {n_pass} pass / {n_warn} warn / {n_fail} fail / {len(results)} total ----")
    return results


def write_json(path: str, results: list[BenchResult]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump([r.as_dict() for r in results], f, indent=2, sort_keys=True)
