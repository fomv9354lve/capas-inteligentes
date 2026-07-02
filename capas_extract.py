# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""CAPAS extract — deterministic table extraction from a PDF, so the number that reaches the gate
came from parsing the source, NOT an LLM re-typing it (the R1 residue). Re-runnable + auditable:
anyone runs the same parse on the same PDF and gets the same rows and the same verdict.
"""
from __future__ import annotations
import re, subprocess

def pdf_page_text(pdf_path: str, page: int) -> str:
    out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), pdf_path, "-"],
                         capture_output=True, text=True, check=True).stdout
    return out.replace("−", "-").replace("±", " ")   # normalise minus + strip '±'

_NUM = re.compile(r"[-+]?\d*\.?\d+")
def extract_c_table(pdf_path: str, page: int, k_vals=(60, 150)) -> list[dict]:
    """Parse the C(x) table (x, k, C_hat, sigma, C_pred, ratio, z) — a line with 7 numbers whose
    first is a fraction in (0,1) and second is a known k."""
    rows = []
    for line in pdf_page_text(pdf_path, page).splitlines():
        nums = [float(t) for t in _NUM.findall(line)]
        if len(nums) == 7 and 0 < nums[0] < 1 and int(nums[1]) in k_vals:
            x, k, ch, sig, pred, ratio, z = nums
            rows.append({"x": x, "k": int(k), "C_hat": ch, "sigma": sig,
                         "C_pred": pred, "ratio": ratio, "z": z})
    return rows
