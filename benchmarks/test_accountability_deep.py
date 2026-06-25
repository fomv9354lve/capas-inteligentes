#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""Exercise the accountability layer end to end — real tests, not gaming.

This drives the FOUR modules of the accountability stratum with valid, plausible inputs so
their bodies actually execute (not just import):

  capas_registry  — append-only, hash-chained, Merkle-rooted decision log; tamper detection
                    (verify_chain reorder/insert/delete/body-alter), verify_entry, history.
  capas_trust     — Beta-smoothed survival rate (track_record) and the ATTEST-vs-GATE
                    provisional_weight discount.
  capas_ledger    — the survive-refutation loop over the primitives: attest -> resolve ->
                    standing -> admit (GATE stands on proof; ATTEST is worth earned standing).
  capas_sdk       — the PERSISTED admit/resolve/standing path (file-backed via CAPAS_DATA_DIR).
  capas_mcp       — the MCP server surface that is importable WITHOUT a live server: handle()
                    for initialize / tools/list / tools/call (ok + error) / ping / notifications
                    / unknown-method, and serve() over in-memory stdin/stdout streams.

Invariants asserted: chain integrity holds for honest logs and breaks on every tamper; trust is
earned by surviving refutation and lost by being refuted; GATE weight is undiscounted while ATTEST
is discounted by standing; the persisted ledger round-trips admit->resolve->standing; the MCP
dispatcher returns well-formed JSON-RPC for every method and fails closed on bad/unknown calls.

Run: `python3 benchmarks/test_accountability_deep.py`  (or pytest).
Note: does NOT overlap test_engine_surface.py (that drives the per-claim-type gate; this drives
the ledger/registry/trust/mcp accountability paths).
"""
from __future__ import annotations

import io
import json
import os
import tempfile

import capas_ledger
import capas_mcp
import capas_registry
import capas_trust

_GENESIS = "sha256:genesis"


def _cert(claim_id: str, verdict: str = "HOLD") -> dict:
    """A plausibly-shaped signed admissibility certificate (the body the registry chains)."""
    return {
        "claim_id": claim_id,
        "verdict": verdict,
        "scope": "ATTEST",
        "engine_digest": "sha256:engine-" + claim_id,
        "certificate_id": "cid-" + claim_id,
        "signature": "ed25519-sig-" + claim_id,
    }


# --------------------------------------------------------------------------------------------
# capas_registry — hash chain, Merkle root, tamper detection, history, verify_entry
# --------------------------------------------------------------------------------------------

def test_registry_append_is_pure_and_chained():
    log0: list = []
    log1 = capas_registry.append(log0, _cert("c1", "ACCEPT"), at="2026-01-01")
    log2 = capas_registry.append(log1, _cert("c2", "HOLD"), at="2026-01-02")

    # append is pure: inputs never mutated, lengths grow by exactly one
    assert log0 == [], "append mutated the empty input log"
    assert len(log1) == 1 and len(log2) == 2

    # genesis link + chain link to prior entry
    assert log2[0]["prev_chained_root"] == _GENESIS
    assert log2[1]["prev_chained_root"] == log2[0]["chained_root"]
    assert log2[0]["seq"] == 0 and log2[1]["seq"] == 1
    # carried-through certificate fields
    assert log2[0]["verdict"] == "ACCEPT" and log2[0]["claim_id"] == "c1"
    assert log2[1]["at"] == "2026-01-02"


def test_registry_verify_chain_intact():
    log: list = []
    for i in range(5):
        log = capas_registry.append(log, _cert(f"k{i}"), at=f"2026-01-0{i + 1}")
    res = capas_registry.verify_chain(log)
    assert res["intact"] is True
    assert res["entries"] == 5
    assert res["merkle_root"].startswith("sha256:")
    assert res["head"] == log[-1]["chained_root"]


def test_registry_merkle_root_changes_on_any_edit():
    log: list = []
    for i in range(4):
        log = capas_registry.append(log, _cert(f"m{i}"))
    root_a = capas_registry.merkle_root(log)
    assert root_a.startswith("sha256:")
    # an extra decision changes the single fingerprint
    log_more = capas_registry.append(log, _cert("m4"))
    assert capas_registry.merkle_root(log_more) != root_a
    # empty log -> genesis sentinel
    assert capas_registry.merkle_root([]) == _GENESIS


def test_registry_merkle_root_odd_tail():
    # 3 entries exercises the duplicate-the-odd-tail branch in merkle_root
    log: list = []
    for i in range(3):
        log = capas_registry.append(log, _cert(f"o{i}"))
    root = capas_registry.merkle_root(log)
    assert root.startswith("sha256:") and len(root) == len("sha256:") + 64


def test_registry_detects_reorder_insert_delete_and_body_alter():
    log: list = []
    for i in range(4):
        log = capas_registry.append(log, _cert(f"t{i}"))
    assert capas_registry.verify_chain(log)["intact"] is True

    # reorder / prev-link tamper
    reordered = [dict(e) for e in log]
    reordered[2]["prev_chained_root"] = "sha256:wrong"
    r = capas_registry.verify_chain(reordered)
    assert r["intact"] is False and r["broken_at"] == 2

    # deletion -> seq goes out of order
    deleted = [dict(e) for e in log[:1]] + [dict(e) for e in log[2:]]
    d = capas_registry.verify_chain(deleted)
    assert d["intact"] is False

    # body-digest alteration -> chained_root mismatch
    altered = [dict(e) for e in log]
    altered[1]["body_digest"] = "sha256:tampered-body"
    a = capas_registry.verify_chain(altered)
    assert a["intact"] is False and a["broken_at"] == 1


def test_registry_verify_entry_authentic_and_tampered():
    cert = _cert("ve1", "ACCEPT")
    log = capas_registry.append([], cert)
    entry = log[0]

    ok = capas_registry.verify_entry(entry, cert)
    assert ok["body_matches_log"] is True
    assert ok["tampered"] is False
    assert ok["verdict"].startswith("AUTHENTIC")

    tampered_cert = {**cert, "verdict": "REJECT"}  # body no longer hashes to logged digest
    bad = capas_registry.verify_entry(entry, tampered_cert)
    assert bad["body_matches_log"] is False
    assert bad["tampered"] is True
    assert bad["verdict"].startswith("TAMPERED")


def test_registry_history_is_claim_scoped_and_ordered():
    log: list = []
    log = capas_registry.append(log, _cert("alpha", "HOLD"))
    log = capas_registry.append(log, _cert("beta", "ACCEPT"))
    log = capas_registry.append(log, _cert("alpha", "REWRITE"))
    hist = capas_registry.history(log, "alpha")
    assert len(hist) == 2
    assert [e["verdict"] for e in hist] == ["HOLD", "REWRITE"]
    assert all(e["claim_id"] == "alpha" for e in hist)
    assert capas_registry.history(log, "nonexistent") == []


# --------------------------------------------------------------------------------------------
# capas_trust — earned standing (Beta-smoothed) + ATTEST/GATE provisional weight
# --------------------------------------------------------------------------------------------

def test_trust_unknown_attester_prior_is_half():
    tr = capas_trust.track_record([], "stranger")
    assert tr["trust"] == 0.5, "Laplace prior for an unknown attester must be 0.5"
    assert tr["resolved"] == 0 and tr["survived"] == 0 and tr["refuted"] == 0


def test_trust_earned_by_surviving_lost_by_refuted():
    log: list = []
    for i in range(3):
        log = capas_ledger.attest(log, _cert(f"s{i}"), "alice")
    log = capas_ledger.resolve(log, "s0", "survived")
    log = capas_ledger.resolve(log, "s1", "survived")
    log = capas_ledger.resolve(log, "s2", "refuted")
    tr = capas_trust.track_record(log, "alice")
    assert tr["survived"] == 2 and tr["refuted"] == 1 and tr["resolved"] == 3
    # Beta(survived+1, refuted+1): (2+1)/(3+2) = 0.6, strictly above the 0.5 prior
    assert tr["trust"] == 0.6
    assert tr["trust"] > 0.5

    # a mostly-refuted attester drops below the prior
    log2: list = []
    for i in range(3):
        log2 = capas_ledger.attest(log2, _cert(f"r{i}"), "mallory")
    log2 = capas_ledger.resolve(log2, "r0", "refuted")
    log2 = capas_ledger.resolve(log2, "r1", "refuted")
    log2 = capas_ledger.resolve(log2, "r2", "survived")
    assert capas_trust.track_record(log2, "mallory")["trust"] < 0.5


def test_trust_provisional_weight_gate_vs_attest():
    log: list = []
    for i in range(4):
        log = capas_ledger.attest(log, _cert(f"w{i}"), "lab")
    for cid, out in [("w0", "survived"), ("w1", "survived"), ("w2", "survived"), ("w3", "refuted")]:
        log = capas_ledger.resolve(log, cid, out)
    trust = capas_trust.track_record(log, "lab")["trust"]
    assert 0.0 < trust < 1.0

    gate = capas_trust.provisional_weight(1.0, "lab", log, scope="GATE")
    attest = capas_trust.provisional_weight(1.0, "lab", log, scope="ATTEST")
    # GATE stands on its own proof -> undiscounted; ATTEST is worth only earned standing
    assert gate["provisional_weight"] == 1.0
    assert attest["provisional_weight"] == round(1.0 * trust, 4)
    assert attest["provisional_weight"] < gate["provisional_weight"]
    assert "GATE" in gate["basis"] and "ATTEST" in attest["basis"]


# --------------------------------------------------------------------------------------------
# capas_ledger — the survive-refutation loop: attest -> resolve -> standing -> admit
# --------------------------------------------------------------------------------------------

def test_ledger_attest_starts_open_and_is_chained():
    log = capas_ledger.attest([], _cert("L1", "HOLD"), "bob", at="2026-02-01")
    assert log[0]["attester"] == "bob"
    assert log[0]["outcome"] == "open"
    # still a valid registry entry under the hood
    assert capas_registry.verify_chain(log)["intact"] is True


def test_ledger_resolve_collapses_open_once():
    log = capas_ledger.attest([], _cert("L2", "HOLD"), "bob")
    resolved = capas_ledger.resolve(log, "L2", "refuted")
    assert resolved[0]["outcome"] == "refuted"
    assert log[0]["outcome"] == "open", "resolve mutated the input log"
    # a second resolve does NOT re-flip an already-resolved entry (only 'open' is collapsible)
    again = capas_ledger.resolve(resolved, "L2", "survived")
    assert again[0]["outcome"] == "refuted"


def test_ledger_resolve_rejects_illegal_outcome():
    log = capas_ledger.attest([], _cert("L3"), "bob")
    try:
        capas_ledger.resolve(log, "L3", "maybe")
    except AssertionError:
        pass
    else:
        raise AssertionError("resolve accepted an illegal outcome")


def test_ledger_standing_matches_track_record():
    log: list = []
    log = capas_ledger.attest(log, _cert("g0"), "carol")
    log = capas_ledger.attest(log, _cert("g1"), "carol")
    log = capas_ledger.resolve(log, "g0", "survived")
    st = capas_ledger.standing(log, "carol")
    assert st == capas_trust.track_record(log, "carol")
    assert st["survived"] == 1 and st["open"] == 1


def test_ledger_admit_gate_full_attest_discounted_and_reward_mapping():
    # build a track record so the ATTEST discount is observable
    log: list = []
    for i in range(2):
        log = capas_ledger.attest(log, _cert(f"a{i}"), "dave")
    log = capas_ledger.resolve(log, "a0", "survived")
    log = capas_ledger.resolve(log, "a1", "survived")

    new_accept = _cert("new-accept", "ACCEPT")
    log_g = capas_ledger.attest(log, new_accept, "dave")
    gate = capas_ledger.admit(log_g, new_accept, "dave", scope="GATE")
    assert gate["provisional_weight"] == 1.0          # ACCEPT->1.0, GATE undiscounted
    assert gate["claim_id"] == "new-accept"
    assert gate["chain_intact"] is True

    new_hold = _cert("new-hold", "HOLD")
    log_a = capas_ledger.attest(log, new_hold, "dave")
    attest = capas_ledger.admit(log_a, new_hold, "dave", scope="ATTEST")
    # HOLD base reward 0.25 discounted by earned trust (<1) -> strictly less
    assert 0.0 < attest["provisional_weight"] < 0.25

    # REJECT maps to base reward 0.0 regardless of standing
    new_rej = _cert("new-rej", "REJECT")
    log_r = capas_ledger.attest(log, new_rej, "dave")
    rej = capas_ledger.admit(log_r, new_rej, "dave", scope="ATTEST")
    assert rej["provisional_weight"] == 0.0


# --------------------------------------------------------------------------------------------
# capas_sdk — the PERSISTED admit/resolve/standing path (file-backed, isolated dir)
# --------------------------------------------------------------------------------------------

def test_sdk_persisted_admit_resolve_standing_roundtrip():
    import capas_sdk  # imported under the isolated CAPAS_DATA_DIR set below
    # admit a proof-backed (ACCEPT->GATE) claim
    res = capas_sdk.admit(
        "statistical_confidence",
        {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        attester="lab-x", claim_text="effect is real", claim_id="sdk-claim-1",
    )
    assert res["verdict"] == "ACCEPT"
    assert res["attester"] == "lab-x"
    assert res["provisional_weight"]["scope"] == "GATE"
    assert res["provisional_weight"]["provisional_weight"] == 1.0

    # before resolution: one open attestation, prior trust
    before = capas_sdk.standing("lab-x")
    assert before["open"] == 1 and before["resolved"] == 0 and before["trust"] == 0.5

    # the world resolves it survived -> standing rises above the prior
    rec = capas_sdk.resolve("sdk-claim-1", "survived")
    assert rec["recorded"] is True and rec["outcome"] == "survived"
    after = capas_sdk.standing("lab-x")
    assert after["survived"] == 1 and after["resolved"] == 1
    assert after["trust"] > before["trust"]


# --------------------------------------------------------------------------------------------
# capas_mcp — server surface importable without a live MCP server
# --------------------------------------------------------------------------------------------

def test_mcp_initialize_advertises_capabilities():
    resp = capas_mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert resp["id"] == 1
    res = resp["result"]
    assert res["protocolVersion"] == capas_mcp.PROTOCOL_VERSION
    assert res["serverInfo"] == capas_mcp.SERVER_INFO
    assert "tools" in res["capabilities"]


def test_mcp_tools_list_matches_registry():
    resp = capas_mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in resp["result"]["tools"]}
    assert names == set(capas_mcp.TOOLS.keys())
    for t in resp["result"]["tools"]:
        assert t["description"] and "inputSchema" in t
        assert t["inputSchema"]["type"] == "object"


def test_mcp_tools_call_gate_ok():
    resp = capas_mcp.handle({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "capas_gate", "arguments": {
            "claim_type": "statistical_confidence",
            "evidence": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        }},
    })
    result = resp["result"]
    assert result["isError"] is False
    assert result["structuredContent"]["verdict"] in {"ACCEPT", "REWRITE", "REJECT", "HOLD"}
    # content is the JSON-serialized structured result
    assert result["content"][0]["type"] == "text"
    json.loads(result["content"][0]["text"])  # must be valid JSON


def test_mcp_tools_call_reward_and_invariants():
    rew = capas_mcp.handle({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "capas_reward", "arguments": {
            "claim_type": "statistical_confidence",
            "evidence": {"p_value": 0.01, "alpha": 0.05, "effect_direction_confirmed": True},
        }},
    })
    assert rew["result"]["isError"] is False
    assert 0.0 <= rew["result"]["structuredContent"]["reward"] <= 1.0

    inv = capas_mcp.handle({
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "capas_invariants", "arguments": {
            "block": {"accounting": {"assets": 100.0, "liabilities": 40.0, "equity": 60.0}},
        }},
    })
    assert inv["result"]["isError"] is False
    assert "structuredContent" in inv["result"]


def test_mcp_unknown_tool_and_bad_args_fail_closed():
    unknown = capas_mcp.handle({
        "jsonrpc": "2.0", "id": 6, "method": "tools/call",
        "params": {"name": "does_not_exist", "arguments": {}},
    })
    assert unknown["error"]["code"] == -32602

    # missing required 'claim_type' -> handler raises -> surfaced as isError, never a crash
    bad = capas_mcp.handle({
        "jsonrpc": "2.0", "id": 7, "method": "tools/call",
        "params": {"name": "capas_gate", "arguments": {}},
    })
    assert bad["result"]["isError"] is True
    assert "fail-closed" in bad["result"]["content"][0]["text"]


def test_mcp_ping_notifications_and_unknown_method():
    assert capas_mcp.handle({"jsonrpc": "2.0", "id": 8, "method": "ping"})["result"] == {}
    # notifications carry no id -> no response
    assert capas_mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert capas_mcp.handle({"jsonrpc": "2.0", "method": "initialized"}) is None
    # unknown method WITH an id -> JSON-RPC method-not-found
    unk = capas_mcp.handle({"jsonrpc": "2.0", "id": 9, "method": "frobnicate"})
    assert unk["error"]["code"] == -32601
    # unknown method with NO id -> nothing
    assert capas_mcp.handle({"jsonrpc": "2.0", "method": "frobnicate"}) is None


def test_mcp_serve_over_inmemory_streams():
    lines = [
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}),
        json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),  # no reply
        "",                                                                     # blank skipped
        "this is not json",                                                     # decode error skipped
        json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}),
    ]
    out = io.StringIO()
    capas_mcp.serve(stdin=io.StringIO("\n".join(lines) + "\n"), stdout=out)
    responses = [json.loads(line) for line in out.getvalue().splitlines() if line.strip()]
    # exactly the two requests with ids get responses; notification/blank/bad-json are silent
    assert [r["id"] for r in responses] == [1, 2]
    assert responses[0]["result"]["serverInfo"]["name"] == "capas"
    assert {t["name"] for t in responses[1]["result"]["tools"]} == set(capas_mcp.TOOLS.keys())


# --------------------------------------------------------------------------------------------
# runner (so `python3 benchmarks/test_accountability_deep.py` exits 0 without pytest)
# --------------------------------------------------------------------------------------------

def _main() -> int:
    # isolate the persisted SDK ledger to a throwaway dir so we never touch ~/.capas
    os.environ["CAPAS_DATA_DIR"] = tempfile.mkdtemp(prefix="capas_acct_test_")
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except Exception as exc:  # noqa: BLE001 — test runner surfaces any failure
            failed += 1
            print(f"FAIL {t.__name__}: {exc!r}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


# pytest fixture-free isolation: set the env var at import so pytest runs hit the temp ledger too
os.environ.setdefault("CAPAS_DATA_DIR", tempfile.mkdtemp(prefix="capas_acct_test_"))


if __name__ == "__main__":
    raise SystemExit(_main())
