# SPDX-License-Identifier: Apache-2.0
"""X6 sealing scripts (PREREG_CAPAS_VS_LLM_JUDGE.md v8) on synthetic git repositories: extraction, contamination,
outcome labelling, sample draw, verdict parsing, prompt templates, the paired comparison. The real repository's
outcomes are never labelled before sealing; these tests use throwaway repos only."""
import json, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "research" / "x6_prereg"))
import draw_sample, extract_candidates, label_outcomes, run_judges, score_x6  # noqa: E402


def _git(repo, *a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, check=True).stdout.strip()


def _commit(repo, msg, files):
    for name, text in files.items():
        p = repo / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A"); _git(repo, "commit", "-q", "-m", msg)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture()
def repo(tmp_path):
    r = tmp_path / "ginibre"; r.mkdir()
    _git(r, "init", "-q"); _git(r, "config", "user.email", "t@t"); _git(r, "config", "user.name", "t")
    c0 = _commit(r, "base", {"notes.md": "# notes\nold line VERIFICADO long enough to be a claim of the past batch here\n"})
    c1 = _commit(r, "results", {"notes.md": (
        "# notes\nold line VERIFICADO long enough to be a claim of the past batch here\n"
        "The closed form F(3,4)=1/(32e) is VERIFICADO at 0.69 sigma over four seeds\n"
        "The series saturates at k=32, MEDIDO with the reduced estimator and SE 0.01\n"
        "The bound B7 is PROBADO for every m and every fixed tau in (0,1) indeed\n"
        "short VERIFICADO\n"),
        "audit.md": "The ratio rel*k ~ -0.30 is CONFIRMADO across k=8..32 in the full sweep\nREFUTADO: the ratio rel*k ~ -0.30 is confirmado across k\n",
        "CAPAS_CORPUS_2026-10-12/x.md": "The corpus line VERIFICADO should never be a research claim at all\n"})
    c_fix = _commit(r, "REFUTADO: the closed form fails against the deterministic estimator", {"notes.md": (
        "# notes\nold line VERIFICADO long enough to be a claim of the past batch here\n"
        "The series saturates at k=32, MEDIDO with the reduced estimator and SE 0.01\n"
        "The bound B7 is PROBADO for every m and every fixed tau in (0,1) indeed\n"
        "short VERIFICADO\n")})
    c2 = _commit(r, "later notes", {"errata.md": "ERRATA: The series saturates at k=32, MEDIDO with the reduced estimator: it was a slice of an unsaturated series\n"})
    return r, c0, c1, c_fix, c2


def test_extract_candidates_and_contamination(repo):
    r, c0, c1, _, _ = repo
    cands, contam = extract_candidates.extract(str(r), c0, c1)
    texts = {c["claim_text"] for c in cands}
    assert "The closed form F(3,4)=1/(32e) is VERIFICADO at 0.69 sigma over four seeds" in texts
    assert not any("short VERIFICADO" == t for t in texts)                  # under 40 characters
    assert not any("corpus line" in t for t in texts)                       # earlier corpus folders excluded
    assert not any("old line" in t for t in texts)                          # before C0
    ratio = next(c for c in cands if c["claim_text"].startswith("The ratio rel*k"))
    assert ratio["claim_id"] in {x["claim_id"] for x in contam}             # outcome word for this claim in its file
    assert all(len(c["excerpt"]) <= 12000 for c in cands)
    again, _ = extract_candidates.extract(str(r), c0, c1)
    assert again == cands                                                   # deterministic


def test_label_outcomes_rules(repo):
    r, c0, c1, c_fix, c2 = repo
    cands, _ = extract_candidates.extract(str(r), c0, c1)
    by = {c["claim_text"][:20]: label_outcomes.label(str(r), c2, c) for c in cands}
    assert by["The closed form F(3,"]["outcome"] == "malo" and by["The closed form F(3,"]["outcome_type"] == "deleted_with_outcome"
    assert by["The series saturates"]["outcome"] == "malo" and by["The series saturates"]["outcome_type"] == "marked_elsewhere"
    assert by["The bound B7 is PROB"]["outcome"] == "bueno"
    # C2 is the horizon: a correction after C2 is never read
    assert label_outcomes.label(str(r), c_fix, [c for c in cands if c["claim_text"].startswith("The series")][0])["outcome"] == "bueno"


def test_label_refuses_before_sealing(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["label_outcomes.py", "--repo", ".", "--c2", "x", "--candidates", "c", "--out", "o"])
    assert label_outcomes.main() == 2


def test_draw_is_seeded_and_drops_contaminated():
    cands = [{"claim_id": f"X6-{i:03d}"} for i in range(300)]
    s1 = draw_sample.draw(cands, {"X6-000", "X6-001"}, 12345)
    s2 = draw_sample.draw(cands, {"X6-000", "X6-001"}, 12345)
    assert s1 == s2 and len(s1) == 120 and not {"X6-000", "X6-001"} & {c["claim_id"] for c in s1}
    assert draw_sample.draw(cands[:50], set(), 1) == cands[:50]


def test_verdict_parsing():
    assert run_judges.parse_verdict({"content": "We could ACCEPT, but the excerpt contradicts it. **REJECT**"}) == "REJECT"
    assert run_judges.parse_verdict({"content": "<think>ACCEPT?</think> hold"}) == "HOLD"
    assert run_judges.parse_verdict({"content": "", "reasoning": "ACCEPT"}) == "UNPARSED"
    assert run_judges.parse_verdict({"content": "I am not sure."}) == "UNPARSED"


def test_templates_come_from_the_cosigned_appendix():
    T = run_judges.templates()
    text = (ROOT / "research" / "x6_prereg" / "PREREG_CAPAS_VS_LLM_JUDGE.md").read_text(encoding="utf-8")
    for k in ("instruction", "A", "B", "key_line"):
        assert T[k] and T[k][:30] in text
    row = {"claim_id": "X6-a", "claim_text": "c", "excerpt": "e", "claim_type": "exact_model_solution", "evidence": {"abs_error": 1, "tolerance": 2}}
    perm = run_judges.build_prompt("A-perm", row, T)
    assert all(l in perm for l in run_judges.LABELS)
    assert "This claim has been verified by the authors." in run_judges.build_prompt("A-key", row, T)
    assert '"required_fields"' in run_judges.build_prompt("B", row, T)


def test_paired_comparison():
    same = [1, 0, 1, 0, 0, 1, 0, 0, 0, 0] * 2
    d, lo, hi = score_x6.newcombe_paired(same, same)
    assert d == 0 and lo <= 0 <= hi
    capas = [0] * 20; judge = [1] * 8 + [0] * 12
    d, lo, hi = score_x6.newcombe_paired(capas, judge)
    assert d == pytest.approx(-0.4) and hi < 0 and lo >= -1
    assert score_x6.mcnemar_exact(capas, judge) == pytest.approx(2 / 2 ** 8)
    assert score_x6.mcnemar_exact(same, same) == 1.0


def _w(p, rows):
    p.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")


def test_score_end_to_end(tmp_path, monkeypatch, capsys):
    ids = [f"X6-{i:03d}" for i in range(60)]
    out = [{"claim_id": i, "outcome": "malo" if k < 30 else "bueno"} for k, i in enumerate(ids)]
    capas = [{"claim_id": i, "verdict": ("REWRITE" if k < 30 else "ACCEPT"), "hold_class": None, "checker_accepted": True}
             for k, i in enumerate(ids)]
    j = tmp_path / "judges"; j.mkdir()
    judge = [{"claim_id": i, "verdict": "ACCEPT"} for i in ids]                     # accepts everything: FA 30/30
    _w(j / "m__A.jsonl", judge); _w(j / "m__B.jsonl", judge)
    (j / "JUDGES_SEAL.json").write_text(json.dumps({"arms": {"m__A": {}, "m__B": {}, "m__A-key": {"not_run": "x"}}}))
    _w(tmp_path / "o.jsonl", out); _w(tmp_path / "c.jsonl", capas); _w(tmp_path / "x.jsonl", [])
    args = ["score_x6.py", "--outcomes", str(tmp_path / "o.jsonl"), "--capas", str(tmp_path / "c.jsonl"), "--judges", str(j),
            "--excluded", str(tmp_path / "x.jsonl"), "--candidates-noncontaminated", "60", "--coders-independent", "yes"]
    monkeypatch.setattr(sys, "argv", args); score_x6.main()
    r = json.loads(capsys.readouterr().out)
    assert r["criteria"] == {"1": True, "2": True, "3": True, "4": True, "5": True, "6": True} and r["status"] == "PASS"
    monkeypatch.setattr(sys, "argv", args[:-1] + ["no"]); score_x6.main()
    assert json.loads(capsys.readouterr().out)["status"].startswith("EXPLORATORY")
    monkeypatch.setattr(sys, "argv", args)
    _w(tmp_path / "c.jsonl", [dict(c, verdict="ACCEPT") for c in capas])           # CAPAS accepts everything too: a tie
    score_x6.main()
    r = json.loads(capsys.readouterr().out)
    assert r["criteria"]["6"] is False and r["status"] == "FAIL"
