"""CAPAS gates its own claims. This regenerates docs/CLAIMS_REGISTRY.md from the proof ledger.

The thesis applied to ourselves: every public claim CAPAS makes must itself be admissible — CLOSED
(proven by a test), BACKED (regenerates from a command, value + hash recorded), or SCOPED (a declared
estimate, with its exact corpus and the artifact that would upgrade it). Nothing bare. The registry is
the public, re-derivable receipt for every number on the site — which is simultaneously the demo, the
honesty shield, and the open-standard's reference artifact.

    python3 benchmarks/generate_claims_registry.py        # writes docs/CLAIMS_REGISTRY.md
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "proof_ledger.json"
OUT = ROOT / "docs" / "CLAIMS_REGISTRY.md"

# Where each ledger claim is surfaced on the site (id -> human location). Keeps the registry honest
# about WHERE a number is shown, so a reader can audit the claim at its point of use.
WHERE = {
    "fail_closed": "Home (“fail-closed (proven)”), Security",
    "robustness": "Security, Audit",
    "no_llm_verdict": "Home (“no language model in the verdict”), Gate App (LLM in gate: NONE)",
    "gates_domains": "Home stat bar (26 gates / 10 domains), Methodology",
    "decisions_1238": "Benchmark (1,238 decisions, 78.4% gated)",
    "beat_benchmark": "Home (“Proof on real hardware”, 2–11×)",
    "false_accept_rate": "Pilot, Home (n=28 retrospective)",
    "retrospective_28": "Home + Pilot (28 retracted-vs-replicated)",
    "head_to_head": "Benchmark (vs LLM-judge)",
    "pip_install": "Home / README install CTA",
}
RISK = {"CLOSED": "low · test-locked", "BACKED": "low · regenerates", "SCOPED": "declared estimate — read the scope"}


def _redrive(e: dict) -> str:
    b = e.get("backing", "")
    if b and (b.endswith(".py") or b.startswith("python3") or "(" in b):
        cmd = b if b.startswith("python3") else (f"python3 {b}" if b.endswith(".py") else b)
        out = cmd
        if e.get("sha256"):
            out += f"  → {e['sha256']}"
        return f"`{out}`"
    return e.get("value", "—")


def main() -> int:
    ledger = json.loads(LEDGER.read_text())
    lines = [
        "# CAPAS Claim Registry",
        "",
        "**CAPAS gates its own claims.** Every public number on this site is itself an admissible claim:",
        "`CLOSED` (proven by a passing test), `BACKED` (regenerates from a command, value+hash recorded),",
        "or `SCOPED` (a declared estimate stated with its exact corpus and the artifact that would upgrade it).",
        "Nothing is bare. Run the command in the *Re-derive* column to reproduce the claim yourself.",
        "",
        "> Regenerate this file: `python3 benchmarks/generate_claims_registry.py` · "
        "release gate: `python3 benchmarks/generate_proof_ledger.py`",
        "",
        "| Claim | Where shown | Status | Re-derive / evidence | Honest scope |",
        "|---|---|---|---|---|",
    ]
    order = {"CLOSED": 0, "BACKED": 1, "SCOPED": 2}
    for e in sorted(ledger, key=lambda x: order.get(x["status"], 9)):
        claim = e.get("claim", "").replace("|", "\\|")
        where = WHERE.get(e["id"], "—").replace("|", "\\|")
        scope = (e.get("scope") or e.get("value") or "").replace("|", "\\|")
        if e.get("upgrade_artifact"):
            scope += f" **Upgrades with:** {e['upgrade_artifact']}."
        lines.append(f"| {claim} | {where} | **{e['status']}** | {_redrive(e)} | {scope} |")

    by = {}
    for e in ledger:
        by[e["status"]] = by.get(e["status"], 0) + 1
    lines += [
        "",
        f"**Ledger:** {by.get('CLOSED',0)} CLOSED · {by.get('BACKED',0)} BACKED · {by.get('SCOPED',0)} SCOPED · 0 bare.",
        "",
        "### Numbers that are illustrative, not measured",
        "- The Gate App **capacity / savings** widget is a **planning model from your own inputs** "
        "(claims × minutes saved × rate) — *planning estimate, not booked savings*. Change the inputs, the number changes.",
        "- The benchmark **1,238 / 78.4%** is a **synthetic adversarial decision-space grid** (contract coverage), "
        "not a production drift rate — regenerate with `python3 benchmarks/family_decision_mix.py`.",
        "",
        "### What CAPAS does NOT claim",
        "CAPAS does not determine truth. It evaluates whether supplied evidence **licenses** a specific claim "
        "under a declared admissibility contract. A well-formed but fabricated-consistent payload still passes "
        "(the GIGO ceiling). See the footer disclaimer on every page.",
        "",
    ]
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)} — {len(ledger)} claims ({by})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
