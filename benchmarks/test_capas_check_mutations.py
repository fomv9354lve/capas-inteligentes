# SPDX-License-Identifier: Apache-2.0
"""Mutated-trace suite (PLAN_v3 A1, council rule-RL member): for every sealed certificate fixture, k mutations
(a rule removed from rules_fired, the verdict flipped, the engine tag altered, the input hash changed, a rule version
bumped in the table); the build fails unless capas_check.py (written from CERTIFICATE_SPEC.md by a separate session
that never read the engine) rejects every one and accepts every unmutated fixture. Checker false-accept must be 0/(k*n)."""
import copy, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import capas_check  # noqa: E402

TABLE = (ROOT / "docs" / "rule_table.json").read_bytes()
FIX = [json.loads(l) for l in (ROOT / "research" / "certificates" / "fixtures.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
OTHER = {"ACCEPT": "REJECT", "REJECT": "ACCEPT", "REWRITE": "ACCEPT", "HOLD": "ACCEPT"}


def _mutations(rec):
    c = rec["certificate"]
    m1 = copy.deepcopy(rec)
    rf = m1["certificate"]["rules_fired"]
    m1["certificate"]["rules_fired"] = rf[:-1] if len(rf) > 1 else ["R0000000000"]
    m2 = copy.deepcopy(rec); m2["certificate"]["verdict"] = OTHER[c["verdict"]]
    m3 = copy.deepcopy(rec); m3["seal"]["engine_tag"] = m3["seal"]["engine_tag"] + "-altered"
    m4 = copy.deepcopy(rec); m4["certificate"]["evidence_sha256"] = "sha256:" + "0" * 64
    m5 = copy.deepcopy(rec); m5.setdefault("payload", {}).setdefault("evidence", {})
    if isinstance(m5["payload"]["evidence"], dict):
        m5["payload"]["evidence"]["__mutated__"] = 1
    else:
        m5["payload"]["evidence"] = {"__mutated__": 1}
    return {"rule_removed": m1, "verdict_flipped": m2, "engine_tag_altered": m3, "input_hash_changed": m4, "payload_changed": m5}


def test_unmutated_fixtures_accepted():
    bad = [r["certificate"]["input_claim"].get("id") for r in FIX if not capas_check.check(r, TABLE)[0]]
    assert not bad, f"checker rejected genuine certificates: {bad[:5]}"


def test_every_mutation_rejected():
    accepted = []
    n = 0
    for rec in FIX:
        for kind, m in _mutations(rec).items():
            n += 1
            if capas_check.check(m, TABLE)[0]:
                accepted.append((rec["certificate"]["input_claim"].get("id"), kind))
    assert n == 5 * len(FIX)
    assert not accepted, f"checker false-accept {len(accepted)}/{n}: {accepted[:5]}"


def test_rule_version_bump_rejected():
    t = json.loads(TABLE)
    t["rules"][0]["version"] += 1
    bumped = (json.dumps(t, indent=1, ensure_ascii=False) + "\n").encode()
    assert not any(capas_check.check(r, bumped)[0] for r in FIX)


def test_checker_does_not_import_the_engine():
    src = (ROOT / "capas_check.py").read_text(encoding="utf-8")
    assert "import capas" not in src and "from capas" not in src
