# SPDX-License-Identifier: Apache-2.0
"""Shared, frozen definitions for the X6 scripts (PREREG_CAPAS_VS_LLM_JUDGE.md, version 8). Hashed with every script
that imports it (seal_prereg.py includes this file in SEAL.json), so a change here is a change to the protocol."""
from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

# §2 Extraction: a line is claim-bearing when it carries one of the project's own assertion markers (the status words
# the Ginibre repository uses to assert a result) and is long enough to state something.
ASSERTION_MARKERS = re.compile(
    r"\b(VERIFICADO|VERIFICADA|VERIFIED|MEDIDO|MEDIDA|MEASURED|PROBADO|PROBADA|PROVEN|PROVED|CERRADO|CERRADA|CLOSED|"
    r"CONFIRMADO|CONFIRMADA|CONFIRMED|DEMOSTRADO|DEMOSTRADA|ESTABLECIDO|ESTABLECIDA|EXACTO|EXACTA|EXACT)\b")
MIN_CLAIM_CHARS = 40
TEXT_SUFFIXES = (".md", ".tex", ".txt")
EXCLUDED_DIRS = ("CAPAS_CORPUS_",)        # the corpus folders of earlier batches are not research claims
EXCERPT_RADIUS = 40                        # lines L-40 .. L+40
EXCERPT_MAX_CHARS = 12000
SAMPLE_MAX = 120

# §2 Outcome rule: the labelling vocabulary (corrected, withdrawn or refuted), fixed here.
OUTCOME_WORDS = re.compile(
    r"\b(REFUTADO|REFUTADA|REFUTED|FALSADO|FALSADA|FALSIFIED|RETRACTADO|RETRACTADA|RETRACTED|RETIRADO|RETIRADA|WITHDRAWN|"
    r"CORREGIDO|CORREGIDA|CORRECTED|ERRATA|ERRATUM|INVALIDADO|INVALIDADA|INVALIDATED|CADUCO|CADUCA|SUPERSEDED|"
    r"REBAJADO|REBAJADA|DOWNGRADED|DESCARTADO|DESCARTADA|DISCARDED|NO SE SOSTIENE|DOES NOT HOLD)\b",
    re.I)
KEY_CHARS = 40                             # a claim is matched in later revisions by its first 40 normalised characters


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: str | Path) -> str:
    return sha256_bytes(Path(p).read_bytes())


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def claim_key(text: str) -> str:
    return norm(text)[:KEY_CHARS]


def git(repo: str | Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


def file_at(repo: str | Path, commit: str, path: str) -> str:
    try:
        return git(repo, "show", f"{commit}:{path}")
    except subprocess.CalledProcessError:
        return ""
