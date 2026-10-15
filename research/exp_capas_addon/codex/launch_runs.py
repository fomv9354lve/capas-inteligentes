"""Run unchanged experiment prompts; record process metadata without reading decisions."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def main():
    runs = []
    for arm in sys.argv[1:]:
        if arm not in ("CA1", "CA2", "CB1", "CB2"):
            raise ValueError(arm)
        directory = HERE / ("arm_A" if arm[1] == "A" else "arm_B")
        directory.mkdir(exist_ok=True)
        if (directory / f"decisions_{arm}.jsonl").exists():
            raise RuntimeError(f"Existing decisions for {arm}; preserve and review before rerun")
        attempt = 1
        while (HERE / f"metadata_{arm}_attempt{attempt}.json").exists():
            attempt += 1
        suffix = "" if attempt == 1 else f"_attempt{attempt}"
        log_path = HERE / f"run_{arm}{suffix}.log"
        meta_path = HERE / f"metadata_{arm}_attempt{attempt}.json"
        prompt_path = HERE / f"prompt_{arm}.md"
        prompt = prompt_path.read_text()
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        command = ["codex", "exec", "--sandbox", "workspace-write", "-C", ".", prompt]
        metadata = {
            "arm": arm, "attempt": attempt, "start": now(), "end": None,
            "wall_seconds": None, "exit_code": None, "log": log_path.name,
            "prompt_sha256": hashlib.sha256(prompt_path.read_bytes()).hexdigest(),
            "cwd": str(ROOT),
            "command": [*command[:-1], f"<unchanged contents of {prompt_path.name}>"],
            "environment_override": {"PYTHONDONTWRITEBYTECODE": "1"},
        }
        start = time.monotonic()
        log = log_path.open("x")
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT)
        metadata["pid"] = process.pid
        meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
        runs.append((process, log, start, metadata, meta_path))
        print(f"{arm}: started attempt {attempt}, pid {process.pid}, at {metadata['start']}", flush=True)
    while runs:
        for run in list(runs):
            process, log, start, metadata, meta_path = run
            code = process.poll()
            if code is None:
                continue
            log.close()
            metadata.update(end=now(), wall_seconds=round(time.monotonic()-start, 3), exit_code=code)
            meta_path.write_text(json.dumps(metadata, indent=2) + "\n")
            print(f"{metadata['arm']}: finished attempt {metadata['attempt']}, exit {code}, "
                  f"wall {metadata['wall_seconds']}s", flush=True)
            runs.remove(run)
        if runs:
            time.sleep(1)


if __name__ == "__main__":
    main()
