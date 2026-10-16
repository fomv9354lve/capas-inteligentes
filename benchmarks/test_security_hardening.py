# SPDX-License-Identifier: Apache-2.0
"""CodeQL triage 2026-10-16: path containment by path (not string prefix), certificate ids, repo reader exclusions,
remote fetches limited to public https hosts, and a linear assertion splitter."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capas  # noqa: E402
import capas_certstore  # noqa: E402
import capas_plan3  # noqa: E402
import capas_rederive  # noqa: E402


def test_source_root_prefix_sibling_is_outside(tmp_path):
    root = tmp_path / "root"; sib = tmp_path / "root2"; root.mkdir(); sib.mkdir()
    (sib / "secret.txt").write_text("x")
    os.symlink(sib, root / "link")                      # resolves to .../root2, which startswith(".../root")
    assert capas_plan3._safe(root.resolve(), "link/secret.txt") is None
    (root / "ok.txt").write_text("y")
    assert capas_plan3._safe(root.resolve(), "ok.txt") is not None
    assert capas_plan3._safe(root.resolve(), "../root2/secret.txt") is None


def test_certificate_ids_never_reach_the_filesystem_unless_well_formed():
    for bad in ("../x", "..", "a/b", "a\\b", "", "x" * 200, None):
        assert capas_certstore.get(bad) is None


def test_repo_reader_refuses_dot_dirs_and_key_material():
    assert capas._safe_local_path(".git/config") is None
    assert capas._safe_local_path("x/.env") is None
    assert capas._safe_local_path("../outside.txt") is None
    assert capas._safe_local_path("README.md") is not None


def test_remote_fetch_only_public_https():
    for url in ("http://example.com/a", "https://127.0.0.1/", "https://169.254.169.254/latest/meta-data/",
                "https://10.0.0.1/", "https://localhost/", "file:///etc/passwd", "https:///nohost", "ftp://x/"):
        assert capas._public_https_url(url) is False, url


def test_assertion_splitter_is_linear_and_unchanged():
    assert capas_rederive.assertion_segments("Mexico grew 20% in Q3, and both entities grew.") == ["Mexico grew 20% in Q3", "both entities grew."]
    assert len(capas_rederive.assertion_segments("Revenue and COGS were 10 and 4 in Q1.")) == 1
    t = time.time()
    capas_rederive.assertion_segments(" " * 4000 + "x"); capas_rederive.assertion_segments(", " * 2000 + "and")
    assert time.time() - t < 0.5
