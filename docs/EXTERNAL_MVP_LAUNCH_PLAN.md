# CAPAS External MVP Launch Plan

Status: local product MVP implemented; external launch path documented.

This file separates what is executable now from what requires an external
account, external user, or standards-community action.

## External MVP Requirements

| Requirement | Current status | Evidence | Remaining work |
|---|---|---|---|
| Clean package install | Implemented and locally fresh-clone smoke-tested | `pyproject.toml`, entrypoint `capas`, `benchmarks/verify_fresh_clone_install.py` | Test from GitHub clone and released artifact after publication |
| Comfortable external input | Implemented with examples, schema, and schema check command | `capas.py decide`, `capas.py check-input`, `docs/schema/capas_claim_payload.schema.json`, `benchmarks/verify_external_input_schema.py` | Expand rule registry after external reviewer feedback |
| UI | Implemented as schema-aware static local HTML | `capas.py ui`, `benchmarks/verify_claim_gate_ui.py`, `outputs/capas_claim_gate_ui.html` | Replace static demo with hosted or packaged app if needed |
| External user validation | Not complete; feedback template and verifier ready | `examples/external_reviewer_feedback_template.json`, `benchmarks/verify_external_user_validation.py`, `outputs/external_user_validation_report.json` | Send minimal packet to one scientific-computation practitioner and store returned feedback in `outputs/external_validation/` |
| Continuous integration | Implemented in repo | `.github/workflows/ci.yml` | Requires GitHub remote/actions to run externally |
| GitHub/release publication | Not complete | release checklist below | Push to GitHub and tag release |
| Formal RO-Crate profile registration | Not complete | local CAPAS profile docs exist | Submit/register profile URI with RO-Crate/Profile registry process |

Current readiness artifacts:

- `outputs/external_reviewer_packet/manifest.json`
- `outputs/profile_registration_packet/manifest.json`
- `outputs/release_readiness_report.json`
- `outputs/fresh_clone_install_report.json`
- `outputs/external_input_schema_report.json`
- `outputs/claim_gate_ui_report.json`
- `outputs/external_user_validation_report.json`
- `outputs/github_release_plan_v0.1.0.json`
- `outputs/release_notes_v0.1.0.md`

Current release readiness result:

```text
release_ready: False
missing: git remote, v0.1.0 tag, valid GitHub CLI authentication
```

## Install

From a fresh clone:

```bash
python -m pip install -e .
capas demo
capas validate
capas inspect trace_039
```

Local fresh-clone smoke test:

```bash
python benchmarks/verify_fresh_clone_install.py
```

Scope: this copies the current source tree into a temporary checkout without
`.git`, build outputs, caches, or installed metadata, installs the package in a
temporary venv with system site packages and
`--no-deps --no-build-isolation`, then runs the venv-local `capas demo`,
`capas decide`, and `capas validate`. It proves the package entrypoint and root
discovery work outside this working tree. It does not prove dependency
resolution from a blank machine or a published GitHub/PyPI artifact.

The package exposes one console script:

```bash
capas
```

## External Claim Input

Example:

```bash
capas schema
capas check-input --input examples/external_claim_accept.json
capas check-input --input examples/external_claim_invalid.json
capas decide --input examples/external_claim_accept.json
capas decide --input examples/external_claim_rewrite.json
capas decide --input examples/external_claim_hold.json
```

Published MVP schema:

```text
docs/schema/capas_claim_payload.schema.json
```

Minimal external payload shape:

```json
{
  "claim": {
    "id": "claim_id",
    "type": "universal_anchor_claim",
    "text": "Claim text"
  },
  "evidence": {
    "anchor_mode": "absolute_anchor",
    "local_property_tests_pass": true,
    "universal_anchor_pass": true
  }
}
```

Supported MVP claim types:

- `exact_model_solution`
- `physical_accuracy`
- `universal_anchor_claim`
- `claim_transition`

Unsupported claim types return `HOLD` rather than being guessed.
Structurally invalid payloads also return `HOLD`, but with `schema_errors`
instead of a claim decision. Missing evidence required for a particular claim
type is not a schema error; it is a claim-evidence insufficiency that the gate
reports as `HOLD`.

## UI

```bash
capas ui
open outputs/capas_claim_gate_ui.html
```

The UI is intentionally static. It is a review surface for the same small rule
gate used by `capas decide`, not an LLM judge. It exposes ACCEPT, REWRITE,
HOLD, and INVALID samples and reports structurally invalid input as `HOLD` with
`schema_errors`.

## External User Validation Packet

Generate/update the packet:

```bash
python scripts/prepare_external_reviewer_packet.py
```

Send a reviewer:

1. `PRODUCT.md`
2. `outputs/capas_product_demo_report.md`
3. `examples/external_claim_accept.json`
4. `examples/external_claim_rewrite.json`
5. `docs/schema/capas_claim_payload.schema.json`
6. command:

```bash
python -m pip install -e .
capas demo
capas check-input --input examples/external_claim_rewrite.json
capas decide --input examples/external_claim_rewrite.json
```

Ask only two questions:

1. Would this evidence/claim split help you audit scientific-computation outputs?
2. Which required field or decision category is missing for your workflow?

External validation is not complete until this feedback changes the schema or
confirms that the schema solves a real audit problem. Returned feedback should
use:

```text
examples/external_reviewer_feedback_template.json
```

Store completed feedback as JSON in:

```text
outputs/external_validation/
```

Then run:

```bash
python benchmarks/verify_external_user_validation.py
```

## GitHub Release Checklist

Prepare release notes and a non-mutating publication plan:

```bash
python scripts/publish_github_release.py
```

The command above is a dry-run. It writes:

- `outputs/github_release_plan_v0.1.0.json`
- `outputs/release_notes_v0.1.0.md`

Check local release readiness:

```bash
python scripts/check_release_readiness.py
```

The check is expected to fail until GitHub remote/auth/tag/release exist.

1. Push repository to GitHub.
2. Confirm GitHub Actions passes `CAPAS CI`.
3. Execute publication only after `git remote -v` and `gh auth status` are valid:

```bash
python scripts/publish_github_release.py --execute
```

4. Release title:

```text
CAPAS Claim Gate v0.1.0 - local evidence-typed claim gate MVP
```

5. Release notes must include:

- local MVP only,
- not fine-tune ready,
- not a new provenance standard,
- not proof of broad LLM scientific reasoning,
- external user validation still pending.

## RO-Crate Profile Registration Path

Generate/update the packet:

```bash
python scripts/prepare_profile_registration_packet.py
```

Current local profile docs:

- `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
- `docs/profile/capas-physical-evidence-context.jsonld`
- `docs/WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md`

Registration is not complete until there is an externally resolvable profile
URI and a registry/community artifact accepting the profile.

Minimum registration packet:

1. Profile name: `CAPAS Physical Evidence Profile`
2. Base standards: RO-Crate 1.1, Workflow Run RO-Crate, PROV-shaped export
3. Extension terms:
   - `capas:physicalEvidenceLevel`
   - `capas:verificationIndependence`
   - `capas:referenceTruth`
   - `capas:evidenceStatus`
   - `capas:claimScope`
4. Example crate:
   - `benchmarks/ro_crates/trace_039/ro-crate-metadata.json`
5. Validator:
   - `benchmarks/validate_capas_profile.py`

## Non-Degradation Rules

- Do not call the external MVP complete until a fresh clone install is tested.
- Do not call user validation complete without an external reviewer artifact.
- Do not call the RO-Crate profile registered until there is an external URI or
  registry entry.
- Do not treat `capas decide` as an LLM or semantic judge; it is a rule gate
  over explicit evidence fields.
