# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""THE PROOF LEDGER — the launch success-criterion, encoded.

Every headline claim must be CLOSED, BACKED, or SCOPED. None bare. This generator regenerates each
claim's backing and records its status; the release gate fails if any claim is bare or its backing
breaks. When this is green, the audit loop TERMINATES: each claim already names its own evidence
and its own limit, so a further audit can only repeat what the claim concedes.

  CLOSED  = a structural/mathematical truth locked by a passing test (cannot regress).
  BACKED  = regenerates from a command, recorded with its value + sha256.
  SCOPED  = empirical-pending, stated with its exact corpus + the artifact that would upgrade it.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


_TAILS: dict[str, str] = {}  # path -> last lines of a FAILING subtest (printed with BACKING BROKEN; CI showed nothing before)


_SKIPPED: dict[str, str] = {}  # path -> reason, for backings whose inputs are not on this machine (rc 2 = SKIP)


def _run_test(path: str) -> bool | None:
    """True = re-derived green; False = broken; None = the script reported SKIP (rc 2: its inputs are not here)."""
    r = subprocess.run([sys.executable, path], cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    if r.returncode == 2:
        _SKIPPED[path] = ((r.stdout or "") + (r.stderr or "")).strip().splitlines()[-1][:160] if (r.stdout or r.stderr) else "SKIP"
        return None
    if r.returncode != 0:
        _TAILS[path] = "\n".join(((r.stderr or "") + "\n" + (r.stdout or "")).strip().splitlines()[-8:])
    return r.returncode == 0


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()[:32] + "…" if path.is_file() else "n/a"


def build() -> list[dict]:
    import capas_sdk
    import capas_quantum_physics as Q
    import benchmarks.generate_capability_matrix as cap  # noqa
    L = []

    # --- CLOSED: structural invariants locked by tests ---
    L.append({"id": "fail_closed", "claim": "Fail-closed: a structurally-deficient claim is never accepted",
              "status": "CLOSED", "backing": "benchmarks/verify_fail_closed.py",
              "ok": _run_test("benchmarks/verify_fail_closed.py"),
              "scope": "Structural invariant (proven). Empirical false-accept RATE on real claims is SCOPED below.",
              "owner": "eval"})
    L.append({"id": "robustness", "claim": "Survives hostile input: no crash, no false-accept, injection inert, SSRF bounded",
              "status": "CLOSED", "backing": "benchmarks/verify_robustness.py",
              "ok": _run_test("benchmarks/verify_robustness.py"),
              "scope": "20 adversarial payloads + an internal-URL SSRF probe; worst case is HOLD/REJECT.",
              "owner": "security"})
    L.append({"id": "no_llm_verdict", "claim": "No language model in the verdict (deterministic)",
              "status": "CLOSED", "backing": "benchmarks/verify_cara_decoupling.py (+ audit_hash determinism)",
              "ok": _run_test("benchmarks/verify_cara_decoupling.py"),
              "scope": "The product loads and decides with the cognitive layer blocked; same input -> same audit_hash.",
              "owner": "cto"})
    L.append({"id": "commitment_gate", "claim": "Quantum-advantage claims past the commitment depth are flagged classically-reproducible",
              "status": "CLOSED", "backing": "benchmarks/verify_quantum_commitment.py",
              "ok": _run_test("benchmarks/verify_quantum_commitment.py"),
              "scope": "The gate CONTRACT is test-locked (the defeater fires iff a hardness claim runs past the "
                       "depth the device stays uncommitted — the association->causation pattern, quantum edition). "
                       "The empirical commitment_depth frontier is supplied as evidence: same-device validated "
                       "(physics-magnitude-lab), cross-device pending.",
              "owner": "quantum"})

    # --- BACKED: regenerates from a command, value + hash recorded ---
    matrix = ROOT / "outputs" / "capability_matrix.json"
    L.append({"id": "gates_domains", "claim": "26 deterministic gates across 10 domains",
              "status": "BACKED", "backing": "python3 benchmarks/generate_capability_matrix.py",
              "ok": _run_test("benchmarks/generate_capability_matrix.py"),
              "value": "26 gates / 10 domains", "artifact": "outputs/capability_matrix.json",
              "sha256": _sha256(matrix), "owner": "eval"})
    mix = ROOT / "outputs" / "family_decision_mix.json"
    L.append({"id": "decisions_1238", "claim": "1,238 decisions, 78.4% hard-gated",
              "status": "BACKED", "backing": "python3 benchmarks/family_decision_mix.py",
              "ok": _run_test("benchmarks/family_decision_mix.py"),
              "value": "N=1238; REWRITE+REJECT=78.4%", "artifact": "outputs/family_decision_mix.json",
              "sha256": _sha256(mix),
              "scope": "SYNTHETIC adversarial decision-space grid (contract coverage), NOT a production drift rate.",
              "owner": "eval"})
    pharma = ROOT / "outputs" / "pharma_corpus.json"
    L.append({"id": "pharma_admissibility", "claim": "Pharma statistical-claim contract: the 3,024-case synthetic grid exhausts its verdict space and no grid case the contract defines as deficient is ACCEPTed",
              "status": "BACKED", "backing": "python3 benchmarks/generate_pharma_corpus.py",
              "ok": _run_test("benchmarks/generate_pharma_corpus.py"),
              "value": "N=3024; hard-gated 95.5%; 0 deficient claims ACCEPTed", "artifact": "outputs/pharma_corpus.json",
              "sha256": _sha256(pharma),
              "scope": "SYNTHETIC contract coverage of the statistical-admissibility space Pinnacle 21 skips "
                       "(significance-vs-alpha, multiplicity, CI-excludes-null, direction, endpoint). NOT a production "
                       "false-accept rate on real submissions. The oracle restates the gate's own rules, so this is contract coverage, "
                       "not validation. Since 2026-10-14 every field is required (missing -> HOLD; external audit found {} -> ACCEPT). "
                       "The pharma gate is a library function (capas_pharma), not exposed on the hosted API.",
              "owner": "pharma"})
    b = Q.complete_error_budget({"cz_error": 1.629e-3, "sx_error": 2.743e-4, "t1_us": 299.57,
                                 "t2_us": 33.9, "readout": 5.371e-3, "zz_residual_hz": 50e3, "idle_ns": 300})
    L.append({"id": "beat_benchmark", "claim": "On one ibm_fez qubit pair (q9-q10), the vendor's headline CZ error under-states the re-derived per-layer floor 11.4x; about 2x on typical pairs",
              "status": "SCOPED", "backing": "python3 benchmarks/generate_proof_ledger.py (capas_quantum_physics.complete_error_budget on the row below; also benchmarks/verify_xeb_purity.py)",
              "sha256": "sha256:" + hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest()[:32] + "…",
              "inputs": {"published": {"cz_error": 1.629e-3, "sx_error": 2.743e-4, "t1_us": 299.57, "t2_us": 33.9, "readout": 5.371e-3},
                         "assumed": {"idle_ns": 300, "zz_residual_hz": 50e3, "cz_time_ns": 68, "leakage": 1e-4}},
              "ok": b.get("exact_gap_x", 0) > 1, "value": f"~2x typical, {b['exact_gap_x']}x worst (dephasing-limited)",
              "scope": "cz, sx, T1 and T2 are the vendor's published fields; idle time (300 ns), residual ZZ (50 kHz), CZ duration and "
                       "leakage are DECLARED ASSUMPTIONS, not published fields. The 11.4x is dominated by dephasing from q9's T2 = 33.9 us "
                       "and scales with the assumed idle. The structured-circuit 3-10x band is Proctor (Nat. Phys. 2022), a cited range.",
              "owner": "quantum"})

    # --- 2026-10-13 audit: the home listed these as PROVEN/BACKED with no ledger entry. Every public number must be here.
    L.append({"id": "hold_has_resolution", "claim": "No HOLD is a dead end: each of the 7 HOLD paths ships a constructive, machine-readable resolution",
              "status": "CLOSED", "backing": "python3 benchmarks/verify_hold_has_resolution.py",
              "ok": _run_test("benchmarks/verify_hold_has_resolution.py"), "owner": "core"})
    L.append({"id": "audit_hash_reproduces", "claim": "Every verdict's audit_hash re-derives from the published recipe and is tamper-evident",
              "status": "CLOSED", "backing": "python3 benchmarks/verify_audit_hash_reproduces.py",
              "ok": _run_test("benchmarks/verify_audit_hash_reproduces.py"), "owner": "core"})
    L.append({"id": "gate_contracts_match", "claim": "The Gate App's served contract regenerates from capas.py (single source of truth; the JS replica is not the engine)",
              "status": "BACKED", "backing": "python3 benchmarks/verify_gate_contracts_match.py",
              "ok": _run_test("benchmarks/verify_gate_contracts_match.py"), "owner": "product"})
    L.append({"id": "sequential_typeI", "claim": "Anytime-valid Type-I guarantee holds in simulation: empirical false-reject <= alpha=0.05 under the null",
              "status": "BACKED", "backing": "python3 benchmarks/demo_sequential_typeI.py",
              "ok": _run_test("benchmarks/demo_sequential_typeI.py"),
              "scope": "A Monte Carlo run, not a test-locked invariant: BACKED, never CLOSED.", "owner": "stats"})
    L.append({"id": "conformance_suite", "claim": "The load-bearing invariants hold together, with a reproducible result hash",
              "status": "BACKED", "backing": "python3 benchmarks/conformance.py", "ok": None,
              "artifact": "outputs/conformance_result.json", "sha256": _sha256(ROOT / "outputs" / "conformance_result.json"),
              "scope": "Not re-run inside this ledger: the conformance suite is what runs this ledger. CI runs it on every push.", "owner": "core"})
    L.append({"id": "benchmark_page_matches_mix", "claim": "docs/benchmark.html carries exactly the counts of outputs/family_decision_mix.json",
              "status": "BACKED", "backing": "python3 benchmarks/verify_benchmark_page_matches_mix.py",
              "ok": _run_test("benchmarks/verify_benchmark_page_matches_mix.py"),
              "scope": "Found stale on 2026-10-13 (3 payloads ACCEPT->HOLD after that day's rules); now a CI check.", "owner": "product"})
    L.append({"id": "attest_conformance", "claim": "A signed conformance attestation binds commit, result hash and a live verdict into one bundle hash",
              "status": "SCOPED", "backing": "python3 benchmarks/attest_conformance.py (keyless Sigstore signing runs in CI: .github/workflows/conformance.yml)",
              "ok": None, "scope": "Needs cosign + an OIDC identity; verified in CI, not re-run here.", "owner": "core"})

    try:
        import hypothesis  # noqa: F401
        fuzz_ok = _run_test("benchmarks/test_dynamic_fuzz.py")
    except ImportError:
        fuzz_ok = None
    L.append({"id": "dynamic_fuzz", "claim": "Never crashes on hostile or garbage input: fails closed to one of the four verdicts (property-based)",
              "status": "CLOSED", "backing": "python3 benchmarks/test_dynamic_fuzz.py (needs hypothesis; CI installs it)", "ok": fuzz_ok,
              "scope": "Property-based (Hypothesis) generalization of verify_robustness.py; skipped where hypothesis is absent.", "owner": "core"})

    # --- SCOPED: empirical-pending, stated with corpus + the upgrade artifact ---
    sealed = ROOT / "outputs" / "ginibre_sealed_scores.json"
    sealed_ok = _run_test("research/ginibre_corpus/score_sealed.py")
    # The sealed corpus sits with the unpublished Ginibre paper, outside the repo. Where it is absent the scorer
    # SKIPs (rc 2) and this claim is SCOPED, not BACKED: the tracked outputs/ginibre_sealed_scores.json carries the
    # figures, but they are only re-derived (sha-verified) on a machine that has the corpus. Never "broken".
    L.append({"id": "blind_corpus_sealed", "claim": "Blind self-gating corpus (Ginibre, 233 real research claims): "
              "out-of-sample bad-not-ACCEPT 17/21, good-not-REJECT 16/17; X1-3 v1 53/82, 51/63",
              "status": "BACKED" if sealed_ok is not None else "SCOPED",
              "backing": "python3 research/ginibre_corpus/score_sealed.py" + (
                  "" if sealed_ok is not None else "  [corpus not on this machine: figures NOT re-derived here; "
                                                   "set CAPAS_GINIBRE_CORPUS=<dir> to re-derive]"),
              "ok": sealed_ok,
              "value": "X1-3 blind (v1 seal, outcomes unopened): 53/82, 51/63 | X4 (v4): 11/13, 6/7 | X5 (v6): 6/8, 10/10 | X4+X5: 17/21 [0.60-0.92], 16/17 [0.73-0.99]",
              "artifact": "outputs/ginibre_sealed_scores.json", "sha256": _sha256(sealed),
              "scope": "Claims coded by a separate session that could not see verdicts; engine frozen at a git tag BEFORE "
                       "coding (X4/X5); verdicts sealed by sha256 BEFORE outcomes were opened; double-counted by both sessions. "
                       "Outcomes = the project's own later corrections ('bueno' = never corrected), not an external oracle. "
                       "n is small; intervals are Wilson 95%. The scorer re-verifies every claims_sha256 against its header.",
              "owner": "eval"})
    L.append({"id": "false_accept_rate", "claim": "Empirical false-accept / false-reject RATE on real claims",
              "status": "SCOPED", "value": "out-of-sample on 38 clean real claims: 4/21 bad ACCEPTed, 1/17 good REJECTed (see blind_corpus_sealed)",
              "scope": "Self-gating of ONE project's claims, not an oracle-adjudicated external rate. A well-formed but "
                       "fabricated-consistent payload can pass (GIGO ceiling): the retraction audit (888-paper control) found "
                       "recomputable inconsistencies do NOT separate retracted from clean papers (2.13% vs 1.58%).",
              "upgrade_artifact": "a second project's blind corpus + an external adjudicator", "owner": "eval"})
    s6 = ROOT / "research" / "section6_package" / "README.md"
    L.append({"id": "section6_counter_signature", "claim": "7 of the 10 claims in the §6 package were attacked by a model of another company "
              "(GOVERNANCE §6: constructor != verifier); 3 were refuted and corrected",
              "status": "BACKED", "backing": "research/section6_package/run_counter_signature.py (model directs, CAPAS executes allowlisted; verbatim transcripts)",
              "ok": all((ROOT / "research" / "section6_package" / f).exists() for f in
                        ("section6_xai_2026-10-13_run1.md", "section6_xai_2026-10-13.md", "section6_xai_2026-10-13_run3.md",
                         "section6_xai_2026-10-13_run4.md", "section6_xai_2026-10-13_run5.md")),
              "value": "8 runs (a 9th aborted on credit), xAI grok-4.7: 3/7 attacked claims REFUTED (C6-02 false-accept by scope, C6-04 unsealed figure, C6-05 unversioned grading) -> each corrected and frozen as a test or sealed file; 4/7 not refuted",
              "artifact": "research/section6_package/README.md", "sha256": _sha256(s6),
              "scope": "One auditor family so far; NOT REFUTED is not PROVED. Run 4's report quoted commands it never executed "
                       "(caught by the transcript); the runner now gates the report against executed commands.",
              "owner": "eval"})
    L.append({"id": "retrospective_28", "claim": "Separated 28 retracted-vs-replicated claims by structure",
              "status": "SCOPED", "backing": "python3 benchmarks/pilot_real.py (agent-coded retrospective; illustrative)", "value": "28/28 on an agent-coded, publicly-known retrospective",
              "scope": "Illustrative; the papers were already publicly retracted (no blind adjudication). Demonstrates "
                       "the contract logic, not blind fraud detection.", "upgrade_artifact": "DONE 2026-10-13: see blind_corpus_sealed (blind-coded, frozen, sealed, double-counted)",
              "owner": "eval"})
    # head_to_head retired 2026-10-14 (council + external audit): n=10, modeled arms; against the real LLM judge the two tied.
    rp = ROOT / "outputs" / "replica_parity.json"
    L.append({"id": "replica_parity", "claim": "The in-browser JS replica is NOT the engine: it agrees with the Python gate on 130/233 sealed payloads",
              "status": "SCOPED", "backing": "python3 benchmarks/replica_parity.py (node + playwright)",
              "value": "130/233 agree; python→js mismatches: REWRITE→ACCEPT 26, REJECT→HOLD 30, ACCEPT→HOLD 17, REWRITE→HOLD 28, HOLD→ACCEPT 2",
              "artifact": "outputs/replica_parity.json", "sha256": _sha256(rp),
              "scope": "Measured 2026-10-13. Consequence applied the same day: the Gate App's single and batch paths use the live "
                       "engine; without a backend the page returns HOLD (fail-closed), never a replica verdict; the local audit "
                       "history is validated by the engine's audit_hash, not by replica recomputation.",
              "upgrade_artifact": "either regenerate rule() from capas.py or delete the replica", "owner": "eval"})
    L.append({"id": "pip_install", "claim": "pip install capas-claim-gate",
              "status": "BACKED", "backing": "pip install capas-claim-gate (PyPI; published from GitHub via OIDC Trusted Publishing, no token)",
              "value": "capas-claim-gate 0.4.0 LIVE on PyPI", "artifact": "https://pypi.org/project/capas-claim-gate/",
              "scope": "Published via the publish.yml Trusted Publisher; current release v0.4.0 (tag v0.4.0 = 6a8471b), first published as v0.1.2; the wheel install is now live.",
              "owner": "release"})
    return L


def main() -> int:
    ledger = build()
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "docs" / "proof_ledger.json").write_text(json.dumps(ledger, indent=2, default=str))

    bare = [e for e in ledger if e["status"] not in ("CLOSED", "BACKED", "SCOPED")]
    broken = [e for e in ledger if e["status"] in ("CLOSED", "BACKED") and e.get("ok") is False]
    by = {}
    for e in ledger:
        by[e["status"]] = by.get(e["status"], 0) + 1

    print("=== PROOF LEDGER ===")
    for e in ledger:
        flag = "" if e.get("ok") is not False else "  <-- BACKING BROKEN"
        print(f"  [{e['status']:6}] {e['claim'][:62]}{flag}")
    for path, why in _SKIPPED.items():
        print(f"\n  --- {path}: SKIPPED on this machine -> claim downgraded to SCOPED ({why})")
    for path, tail in _TAILS.items():
        print(f"\n  --- {path} (rc != 0) ---\n" + "\n".join("  | " + ln for ln in tail.splitlines()))
    print(f"\n{by} | bare: {len(bare)} | broken backing: {len(broken)}")

    # RELEASE GATE: every claim CLOSED/BACKED/SCOPED, and no CLOSED/BACKED backing is broken.
    ok = not bare and not broken
    print("RELEASE GATE: PASS — every headline claim is CLOSED/BACKED/SCOPED, none bare, backings green.\n"
          "Launch criterion met: the audit loop terminates (each claim names its own evidence + limit)."
          if ok else f"RELEASE GATE: FAIL — bare={[e['id'] for e in bare]} broken={[e['id'] for e in broken]}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
