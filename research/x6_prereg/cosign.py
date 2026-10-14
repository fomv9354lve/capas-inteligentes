#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Asks a model from another company (GOVERNANCE §6) to co-sign PREREG_CAPAS_VS_LLM_JUDGE.md or list blocking
objections. Appends the exchange to COSIGN_LOG.md. The model reviews the document only; it has no tools.
Keys: ~/.config/estandar/<provider>.key. Run: python3 research/x6_prereg/cosign.py [xai|gemini|deepseek] [--model M]"""
import datetime, hashlib, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC = HERE / "PREREG_CAPAS_VS_LLM_JUDGE.md"
LOG = HERE / "COSIGN_LOG.md"
PROVIDERS = {"xai": ("https://api.x.ai/v1/chat/completions", "xai.key", "grok-4.7"),
             "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "gemini.key", "gemini-3.8-flash"),
             "deepseek": ("https://api.deepseek.com/chat/completions", "deepseek.key", "deepseek-reasoner")}
SYSTEM = ("You are the opposing reviewer of a pre-registration, in the Hungarian adversarial-collaboration tradition: "
          "the opponent co-signs the protocol before any data exist. The authors built the system under test (CAPAS). "
          "Look for anything that would let them claim success they did not earn: thresholds, exclusions, arms, "
          "measures, sealing order, label bias, coder independence. Reply ONLY with JSON: "
          '{"decision": "CO-SIGN" | "OBJECT", "blocking_objections": [{"section": "...", "objection": "...", '
          '"required_change": "..."}], "non_blocking_notes": ["..."]}. CO-SIGN only if no blocking objection remains.')


def main() -> int:
    prov = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "xai"
    url, keyf, model = PROVIDERS[prov]
    if "--model" in sys.argv:
        model = sys.argv[sys.argv.index("--model") + 1]
    key = (Path.home() / ".config" / "estandar" / keyf).read_text().strip()
    text = DOC.read_text(encoding="utf-8")
    sha = hashlib.sha256(text.encode()).hexdigest()
    body = {"model": model, "temperature": 0, "messages": [{"role": "system", "content": SYSTEM},
                                                            {"role": "user", "content": text}]}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "Authorization": f"Bearer {key}", "User-Agent": "capas-cosign/1.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=300).read())
    reply = d["choices"][0]["message"]["content"]
    served = d.get("model", model)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n## {datetime.datetime.now().isoformat(timespec='seconds')} · {prov} / {served} · prereg sha256 {sha}\n\n```json\n{reply.strip()}\n```\n")
    print(reply)
    try:
        dec = json.loads(reply.strip().removeprefix("```json").removesuffix("```").strip())["decision"]
    except Exception:
        dec = "UNPARSEABLE"
    print(f"\ndecision: {dec} | model {served} | prereg sha256 {sha[:16]}")
    return 0 if dec == "CO-SIGN" else 1


if __name__ == "__main__":
    sys.exit(main())
