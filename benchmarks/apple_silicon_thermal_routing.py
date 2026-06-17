from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from router.trace import stable_hash


@dataclass(frozen=True)
class BackendResult:
    backend: str
    device: str
    state: str
    size: int
    trials: int
    times_s: list[float]
    median_s: float
    min_s: float
    max_s: float
    result_fingerprint: str
    ok: bool = True
    error: str | None = None


def _median(xs: list[float]) -> float:
    return float(statistics.median(xs)) if xs else float("nan")


def _load_backends(size: int) -> dict[str, Callable[[int], Any]]:
    backends: dict[str, Callable[[int], Any]] = {}

    try:
        import numpy as np

        a_np = np.ones((size, size), dtype=np.float32)
        b_np = np.full((size, size), 0.5, dtype=np.float32)

        def numpy_accelerate(_: int) -> Any:
            return a_np @ b_np

        backends["numpy_accelerate_cpu"] = numpy_accelerate
    except Exception as exc:
        backends["numpy_accelerate_cpu"] = _missing_backend("numpy", exc)

    try:
        import mlx.core as mx

        a_mx = mx.ones((size, size), dtype=mx.float32)
        b_mx = mx.full((size, size), 0.5, dtype=mx.float32)

        def mlx_cpu(_: int) -> Any:
            mx.set_default_device(mx.cpu)
            out = a_mx @ b_mx
            mx.eval(out)
            return out

        def mlx_gpu(_: int) -> Any:
            mx.set_default_device(mx.gpu)
            out = a_mx @ b_mx
            mx.eval(out)
            return out

        backends["mlx_cpu"] = mlx_cpu
        backends["mlx_gpu_metal"] = mlx_gpu
    except Exception as exc:
        backends["mlx_cpu"] = _missing_backend("mlx", exc)
        backends["mlx_gpu_metal"] = _missing_backend("mlx", exc)

    return backends


def _missing_backend(name: str, exc: Exception) -> Callable[[int], Any]:
    def _run(_: int) -> Any:
        raise RuntimeError(f"{name} unavailable: {type(exc).__name__}: {exc}")

    return _run


def _fingerprint_result(result: Any) -> str:
    if hasattr(result, "shape"):
        try:
            import numpy as np

            arr = np.asarray(result)
            sample = {
                "shape": tuple(int(x) for x in arr.shape),
                "dtype": str(arr.dtype),
                "first": float(arr.flat[0]) if arr.size else None,
                "last": float(arr.flat[-1]) if arr.size else None,
                "mean": float(arr.mean()) if arr.size else None,
            }
            return stable_hash(sample)
        except Exception:
            pass
    return stable_hash(repr(result)[:500])


def _time_backend(
    backend: str,
    fn: Callable[[int], Any],
    *,
    device: str,
    state: str,
    size: int,
    trials: int,
    warmups: int,
) -> BackendResult:
    times: list[float] = []
    fingerprint = ""
    try:
        for _ in range(max(0, warmups)):
            fn(size)
        for _ in range(trials):
            t0 = time.perf_counter()
            result = fn(size)
            dt = time.perf_counter() - t0
            times.append(float(dt))
            fingerprint = _fingerprint_result(result)
        return BackendResult(
            backend=backend,
            device=device,
            state=state,
            size=size,
            trials=trials,
            times_s=times,
            median_s=_median(times),
            min_s=float(min(times)),
            max_s=float(max(times)),
            result_fingerprint=fingerprint,
        )
    except Exception as exc:
        return BackendResult(
            backend=backend,
            device=device,
            state=state,
            size=size,
            trials=trials,
            times_s=times,
            median_s=float("nan"),
            min_s=float("nan"),
            max_s=float("nan"),
            result_fingerprint=fingerprint,
            ok=False,
            error=f"{type(exc).__name__}: {exc}",
        )


def _device_for_backend(backend: str) -> str:
    if "gpu" in backend:
        return "apple_metal_gpu"
    if "mlx" in backend:
        return "apple_mlx_cpu"
    return "apple_accelerate_cpu"


def _sleep_with_note(seconds: float, label: str) -> None:
    if seconds <= 0:
        return
    print(f"{label}: sleeping {seconds:.1f}s")
    time.sleep(seconds)


def _heat(backends: dict[str, Callable[[int], Any]], backend: str, seconds: float, size: int) -> dict[str, Any]:
    if seconds <= 0:
        return {"backend": backend, "seconds": 0.0, "iterations": 0, "ok": True}
    fn = backends[backend]
    start = time.perf_counter()
    iterations = 0
    try:
        while time.perf_counter() - start < seconds:
            fn(size)
            iterations += 1
        elapsed = time.perf_counter() - start
        return {"backend": backend, "seconds": elapsed, "iterations": iterations, "ok": True}
    except Exception as exc:
        return {
            "backend": backend,
            "seconds": time.perf_counter() - start,
            "iterations": iterations,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _rank(results: list[BackendResult]) -> list[BackendResult]:
    return sorted((r for r in results if r.ok), key=lambda r: r.median_s)


def _winner_margin(ranked: list[BackendResult]) -> float | None:
    if len(ranked) < 2:
        return None
    best = ranked[0].median_s
    second = ranked[1].median_s
    if best <= 0:
        return None
    return float((second - best) / best)


def run(args: argparse.Namespace) -> dict[str, Any]:
    backends = _load_backends(args.size)
    selected = [b for b in args.backends.split(",") if b]
    unknown = sorted(set(selected) - set(backends))
    if unknown:
        raise ValueError(f"unknown backend(s): {unknown}; available={sorted(backends)}")

    _sleep_with_note(args.cooldown_s, "cold protocol")
    cold = [
        _time_backend(
            b,
            backends[b],
            device=_device_for_backend(b),
            state="cold",
            size=args.size,
            trials=args.trials,
            warmups=args.warmups,
        )
        for b in selected
    ]

    heat = _heat(backends, args.heat_backend, args.heat_s, args.heat_size or args.size)
    hot = [
        _time_backend(
            b,
            backends[b],
            device=_device_for_backend(b),
            state="hot_after_sustained_load",
            size=args.size,
            trials=args.trials,
            warmups=args.warmups,
        )
        for b in selected
    ]

    cold_rank = _rank(cold)
    hot_rank = _rank(hot)
    cold_best = cold_rank[0].backend if cold_rank else None
    hot_best = hot_rank[0].backend if hot_rank else None
    thermal_crossover = bool(cold_best and hot_best and cold_best != hot_best)
    cold_margin = _winner_margin(cold_rank)
    hot_margin = _winner_margin(hot_rank)
    meaningful_crossover = bool(
        thermal_crossover
        and cold_margin is not None
        and hot_margin is not None
        and cold_margin >= args.min_margin
        and hot_margin >= args.min_margin
    )

    payload = {
        "benchmark": "apple_silicon_thermal_routing",
        "claim_under_test": (
            "Does sustained Apple Silicon load change the optimal backend choice? "
            "If yes, thermal-aware routing has product value; if no, a static router is enough."
        ),
        "platform": {
            "machine": platform.machine(),
            "platform": platform.platform(),
            "processor": platform.processor(),
        },
        "protocol": {
            "size": args.size,
            "trials": args.trials,
            "warmups": args.warmups,
            "cooldown_s": args.cooldown_s,
            "heat_s": args.heat_s,
            "heat_backend": args.heat_backend,
            "heat_size": args.heat_size or args.size,
            "backends": selected,
            "note": "Use --cooldown-s 90 for the controlled protocol suggested by the M4 thermal study.",
        },
        "heat": heat,
        "cold_results": [asdict(r) for r in cold],
        "hot_results": [asdict(r) for r in hot],
        "decision": {
            "cold_best": cold_best,
            "hot_best": hot_best,
            "thermal_crossover": thermal_crossover,
            "min_margin": args.min_margin,
            "cold_winner_margin": cold_margin,
            "hot_winner_margin": hot_margin,
            "meaningful_crossover": meaningful_crossover,
            "interpretation": (
                "thermal-aware routing is strongly justified by this workload"
                if meaningful_crossover
                else (
                    "backend inversion observed, but at least one winner margin is below threshold"
                    if thermal_crossover
                    else "no backend inversion observed for this workload; static routing may be enough"
                )
            ),
        },
    }
    payload["trace_hash"] = stable_hash(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=1024)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--cooldown-s", type=float, default=0.0)
    parser.add_argument("--heat-s", type=float, default=10.0)
    parser.add_argument("--heat-size", type=int, default=0)
    parser.add_argument("--heat-backend", default="mlx_gpu_metal")
    parser.add_argument("--min-margin", type=float, default=0.10)
    parser.add_argument(
        "--backends",
        default="numpy_accelerate_cpu,mlx_cpu,mlx_gpu_metal",
        help="Comma-separated backend list.",
    )
    parser.add_argument(
        "--out",
        default="benchmarks/apple_silicon_thermal_routing_results.json",
    )
    args = parser.parse_args()
    payload = run(args)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload["decision"], indent=2, sort_keys=True))
    print(f"results written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
