#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""X6 judge harness (PREREG §3 and Appendix A). Runs the eight judge arms on the coded sample and seals their verdicts.

The prompt templates are READ from Appendix A of PREREG_CAPAS_VS_LLM_JUDGE.md at run time (never retyped here), so the
templates the judges see are byte-for-byte the co-signed ones; judge_prompts_sha256 is computed over that appendix.

Arms: {gemini-3.8-flash, openai/gpt-oss-120b} x {A, B, A-perm, A-key}. Parameters: temperature 0, top_p 1, at most 1,024
output tokens, seed 20261014 where accepted, reasoning_effort low for gpt-oss-120b, one call per claim per arm, retries
only on transport errors (network failure, HTTP 429/5xx), never on an answer. Parsing: message.content only, reasoning
fields and <think> blocks discarded, last case-insensitive match of ACCEPT|REWRITE|REJECT|HOLD after markdown markers are
removed; no match -> UNPARSED (counts as HOLD); an arm with more than 10 % UNPARSED is reported as not run.

Input: the coded sample (JSONL): {claim_id, claim_text, excerpt, claim_type, evidence}.
Output: <out>/<model>__<arm>.jsonl (claim_id, verdict, content_sha256, content) and <out>/JUDGES_SEAL.json (sha256 of
every arm file, written before any outcome is labelled).
Run: python3 research/x6_prereg/run_judges.py --sample coded.jsonl --out judges/ [--dry]"""
from __future__ import annotations

import argparse, hashlib, json, random, re, sys, time, urllib.error, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
PREREG = HERE / "PREREG_CAPAS_VS_LLM_JUDGE.md"
MODELS = {
    "gemini-3.8-flash": ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "gemini.key", {}),
    "openai/gpt-oss-120b": ("https://api.groq.com/openai/v1/chat/completions", "groq.key", {"reasoning_effort": "low"}),
}
ARMS = ("A", "B", "A-perm", "A-key")
LABELS = ("ACCEPT", "REWRITE", "REJECT", "HOLD")
VERDICT_RE = re.compile(r"\b(ACCEPT|REWRITE|REJECT|HOLD)\b", re.I)


def appendix() -> str:
    text = PREREG.read_text(encoding="utf-8")
    return text[text.index("## Appendix A. Judge prompt templates (verbatim)"):]


def judge_prompts_sha256() -> str:
    return hashlib.sha256(appendix().encode("utf-8")).hexdigest()


def _quote_after(marker: str, text: str) -> str:
    """The '> ' blockquote that follows `marker`, joined into one paragraph."""
    i = text.index(marker) + len(marker)
    lines, started = [], False
    for line in text[i:].splitlines():
        if line.startswith(">"):
            started = True
            lines.append(line[1:].strip())
        elif started:
            break
    return " ".join(lines)


def templates() -> dict[str, str]:
    a = appendix()
    return {"instruction": _quote_after("Every template ends with the same instruction:", a),
            "A": _quote_after("**Judge A.**", a), "B": _quote_after("**Judge B.**", a),
            "key_line": _quote_after("**Judge A-key.**", a)}


def permuted_instruction(instruction: str, claim_id: str) -> str:
    """Judge A-perm: the four labels (with their definitions) in an order fixed by the claim id."""
    head, _, rest = instruction.partition(": ")
    parts = re.findall(r"(ACCEPT|REWRITE|REJECT|HOLD) \(([^)]*)\)", rest)
    order = list(parts)
    random.Random(claim_id).shuffle(order)
    body = ", ".join(f"{l} ({d})" for l, d in order[:-1]) + f" or {order[-1][0]} ({order[-1][1]})."
    return f"{head}: {body}"


def build_prompt(arm: str, row: dict, T: dict[str, str]) -> str:
    if arm == "B":
        sys.path.insert(0, str(HERE.parents[1]))
        import capas
        contract = json.dumps(capas.requirements_for_claim(row["claim_type"]), ensure_ascii=False, sort_keys=True)
        body = (T["B"].replace("{claim_type}", row["claim_type"]).replace("{contract}", contract)
                .replace("{evidence_json}", json.dumps(row["evidence"], ensure_ascii=False, sort_keys=True)))
        return body + "\n\n" + T["instruction"]
    body = T["A"].replace("{claim_text}", row["claim_text"]).replace("{excerpt}", row["excerpt"])
    if arm == "A-key":
        body = body.replace("Does the evidence", T["key_line"] + " Does the evidence", 1)
    instr = permuted_instruction(T["instruction"], row["claim_id"]) if arm == "A-perm" else T["instruction"]
    return body + "\n\n" + instr


def parse_verdict(message: dict) -> str:
    content = message.get("content") or ""
    content = re.sub(r"<think>.*?</think>", " ", content, flags=re.S | re.I)
    content = re.sub(r"[*_`#>~]", " ", content)
    hits = VERDICT_RE.findall(content)
    return hits[-1].upper() if hits else "UNPARSED"


def call(model: str, prompt: str, key: str) -> dict:
    url, _, extra = MODELS[model]
    body = {"model": model, "temperature": 0, "top_p": 1, "max_tokens": 1024, "seed": 20261014,
            "messages": [{"role": "user", "content": prompt}], **extra}
    for attempt in range(4):
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json",
                                     "Authorization": f"Bearer {key}", "User-Agent": "capas-x6-judges/1.0"})
        try:
            return json.loads(urllib.request.urlopen(req, timeout=120).read())["choices"][0]["message"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt * 5); continue
            if e.code == 400 and "seed" in body:              # an endpoint that rejects the seed parameter
                body.pop("seed"); continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < 3:
                time.sleep(2 ** attempt * 5); continue
            raise
    raise RuntimeError("transport retries exhausted")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--dry", action="store_true", help="build and print the prompts for the first claim; no network")
    a = ap.parse_args()
    rows = [json.loads(l) for l in Path(a.sample).read_text(encoding="utf-8").splitlines() if l.strip()]
    T = templates()
    if a.dry:
        for arm in ARMS:
            print(f"--- {arm}\n{build_prompt(arm, rows[0], T)}\n")
        print("judge_prompts_sha256", judge_prompts_sha256())
        return 0
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    seal = {"judge_prompts_sha256": judge_prompts_sha256(), "sample_sha256": hashlib.sha256(Path(a.sample).read_bytes()).hexdigest(),
            "arms": {}}
    for model, (_, keyf, _) in MODELS.items():
        key = (Path.home() / ".config" / "estandar" / keyf).read_text().strip()
        for arm in ARMS:
            name = f"{model.replace('/', '_')}__{arm}"
            res, not_run = [], None
            for r in rows:
                try:
                    msg = call(model, build_prompt(arm, r, T), key)
                except urllib.error.HTTPError as e:
                    if e.code == 404:                       # model id retired: the arm is not run, never replaced
                        not_run = f"model unavailable (HTTP 404)"; break
                    raise
                content = msg.get("content") or ""
                res.append({"claim_id": r["claim_id"], "verdict": parse_verdict(msg), "content": content,
                            "content_sha256": hashlib.sha256(content.encode()).hexdigest()})
            unparsed = sum(x["verdict"] == "UNPARSED" for x in res)
            if not not_run and res and unparsed / len(res) > 0.10:
                not_run = f"{unparsed}/{len(res)} UNPARSED (> 10 %)"
            body = "".join(json.dumps(x, ensure_ascii=False, sort_keys=True) + "\n" for x in res).encode()
            (out / f"{name}.jsonl").write_bytes(body)
            seal["arms"][name] = {"n": len(res), "unparsed": unparsed, "not_run": not_run, "sha256": hashlib.sha256(body).hexdigest()}
            print(name, seal["arms"][name])
    (out / "JUDGES_SEAL.json").write_text(json.dumps(seal, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
