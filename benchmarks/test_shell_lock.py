# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Fco. Osvaldo Morales Vilchis
"""The shell lock must catch a consumer whose copy drifted from the brand's."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "designlab"))
from layout_lint import shell_lock_drift  # noqa: E402

LOCKED = ("kreniq-shell.css", "lang.js")


def _setup(tmp: Path, css: bytes = b"a{}", js: bytes = b"var a;") -> tuple[Path, Path]:
    docs = tmp / "docs"
    docs.mkdir()
    (docs / "kreniq-shell.css").write_bytes(css)
    (docs / "lang.js").write_bytes(js)
    lock = tmp / "shell.lock.json"
    lock.write_text(json.dumps({
        "kreniq-shell.css": hashlib.sha256(css).hexdigest(),
        "lang.js": hashlib.sha256(js).hexdigest(),
    }))
    return docs, lock


def test_in_sync_reports_no_drift(tmp_path):
    docs, lock = _setup(tmp_path)
    assert shell_lock_drift(docs, lock) == []


def test_edited_css_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    (docs / "kreniq-shell.css").write_bytes(b"a{color:red}")
    drift = shell_lock_drift(docs, lock)
    assert any("kreniq-shell.css" in d for d in drift)


def test_missing_consumer_file_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    (docs / "lang.js").unlink()
    drift = shell_lock_drift(docs, lock)
    assert any("lang.js" in d for d in drift)


def test_missing_lock_is_caught(tmp_path):
    docs, lock = _setup(tmp_path)
    lock.unlink()
    drift = shell_lock_drift(docs, lock)
    assert any("lock" in d.lower() for d in drift)
