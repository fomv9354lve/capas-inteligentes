from __future__ import annotations

import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "profile_registration_packet"

PROFILE_URI = "https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1"

FILES = [
    ("CAPAS_PHYSICAL_EVIDENCE_PROFILE.md", ROOT / "docs" / "profile" / "CAPAS_PHYSICAL_EVIDENCE_PROFILE.md"),
    ("capas-physical-evidence-context.jsonld", ROOT / "docs" / "profile" / "capas-physical-evidence-context.jsonld"),
    ("capas-profile-registration.json", ROOT / "docs" / "profile" / "capas-profile-registration.json"),
    ("RO_CRATE_PROFILE_REGISTRATION_ISSUE.md", ROOT / "docs" / "profile" / "RO_CRATE_PROFILE_REGISTRATION_ISSUE.md"),
    ("WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md", ROOT / "docs" / "WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md"),
    ("trace_039-ro-crate-metadata.json", ROOT / "benchmarks" / "ro_crates" / "trace_039" / "ro-crate-metadata.json"),
    ("validate_capas_profile.py", ROOT / "benchmarks" / "validate_capas_profile.py"),
]


REQUEST = f"""# CAPAS Physical Evidence Profile Registration Request Draft

Profile name: CAPAS Physical Evidence Profile

Draft profile URI:

```text
{PROFILE_URI}
```

Base profiles:

- RO-Crate 1.1
- Process Run Crate 0.5
- Workflow Run Crate 0.5
- Workflow RO-Crate 1.0

Purpose:

CAPAS extends Workflow Run RO-Crate-style scientific computation traces with a
first-class `capas:PhysicalEvidence` entity. The entity records physical
evidence level, witness independence, reference truth, evidence status, claim
scope, local oracle outcome, universal-anchor outcome, and failure/rejection
states.

Non-claim:

CAPAS does not replace RO-Crate, PROV, Workflow Run RO-Crate, Metamorphic
Testing, or VVUQ. It proposes a domain-specific profile for evidence-typed
scientific-computation claim gating.

Registration question:

Is this best represented as:

1. a RO-Crate profile,
2. a Workflow Run RO-Crate sub-profile,
3. an application profile documented outside the registry,
4. or a smaller vocabulary extension?

Included example:

- `trace_039-ro-crate-metadata.json`

Local validator:

- `validate_capas_profile.py`

Registration metadata and issue template:

- `capas-profile-registration.json`
- `RO_CRATE_PROFILE_REGISTRATION_ISSUE.md`

Important:

This packet is a draft submission aid. It is not evidence of formal
registration.
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    copied = []
    missing = []
    for label, src in FILES:
        if not src.exists():
            missing.append(str(src.relative_to(ROOT)))
            continue
        dst = OUT / label
        shutil.copy2(src, dst)
        copied.append(label)

    (OUT / "REGISTRATION_REQUEST.md").write_text(REQUEST, encoding="utf-8")
    copied.append("REGISTRATION_REQUEST.md")

    manifest = {
        "packet": "profile_registration_packet",
        "status": "ready" if not missing else "incomplete",
        "profile_status": "local_draft_not_registered",
        "formal_registration_complete": False,
        "profile_name": "CAPAS Physical Evidence Profile",
        "draft_profile_uri": PROFILE_URI,
        "base_profiles": [
            "https://w3id.org/ro/crate/1.1",
            "https://w3id.org/ro/wfrun/process/0.5",
            "https://w3id.org/ro/wfrun/workflow/0.5",
            "https://w3id.org/workflowhub/workflow-ro-crate/1.0",
        ],
        "copied": copied,
        "missing": missing,
        "completion_rule": (
            "Formal registration is complete only when an external registry, "
            "community process, or stable profile URI accepts the profile."
        ),
        "next_external_action": (
            "Open RO_CRATE_PROFILE_REGISTRATION_ISSUE.md with the Workflow Run "
            "RO-Crate / RO-Crate community and update formal_registration_complete "
            "only after external acceptance."
        ),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(f"profile registration packet: {manifest['status']}")
    print(f"wrote {OUT}")
    if missing:
        print("missing:")
        for item in missing:
            print(f"  {item}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
