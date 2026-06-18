# CAPAS External MVP Launch Plan

Status: local product MVP implemented; external launch path documented.

This file separates what is executable now from what requires an external
account, external user, or standards-community action.

## External MVP Requirements

| Requirement | Current status | Evidence | Remaining work |
|---|---|---|---|
| Clean package install | Implemented and locally fresh-clone smoke-tested | `pyproject.toml`, entrypoint `capas`, `benchmarks/verify_fresh_clone_install.py` | Test from GitHub clone and released artifact after publication |
| Comfortable external input | Implemented for small JSON claim/evidence files | `capas.py decide`, `examples/external_claim_*.json` | Expand rule registry and publish JSON schema |
| UI | Implemented as static local HTML | `capas.py ui` writes `outputs/capas_claim_gate_ui.html` | Replace static demo with hosted or packaged app if needed |
| External user validation | Not complete | no external feedback artifact yet | Send minimal packet to one scientific-computation practitioner |
| Continuous integration | Implemented in repo | `.github/workflows/ci.yml` | Requires GitHub remote/actions to run externally |
| GitHub/release publication | Not complete | release checklist below | Push to GitHub and tag release |
| Formal RO-Crate profile registration | Not complete | local CAPAS profile docs exist | Submit/register profile URI with RO-Crate/Profile registry process |

Current readiness artifacts:

- `outputs/external_reviewer_packet/manifest.json`
- `outputs/profile_registration_packet/manifest.json`
- `outputs/release_readiness_report.json`
- `outputs/fresh_clone_install_report.json`

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

Scope: this clones the current local repository into a temporary directory,
installs the package in a temporary venv with system site packages and
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
capas decide --input examples/external_claim_accept.json
capas decide --input examples/external_claim_rewrite.json
capas decide --input examples/external_claim_hold.json
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

## UI

```bash
capas ui
open outputs/capas_claim_gate_ui.html
```

The UI is intentionally static. It is a review surface for the same small rule
gate used by `capas decide`, not an LLM judge.

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
5. command:

```bash
python -m pip install -e .
capas demo
capas decide --input examples/external_claim_rewrite.json
```

Ask only two questions:

1. Would this evidence/claim split help you audit scientific-computation outputs?
2. Which required field or decision category is missing for your workflow?

External validation is not complete until this feedback changes the schema or
confirms that the schema solves a real audit problem.

## GitHub Release Checklist

Check local release readiness:

```bash
python scripts/check_release_readiness.py
```

The check is expected to fail until GitHub remote/auth/tag/release exist.

1. Push repository to GitHub.
2. Confirm GitHub Actions passes `CAPAS CI`.
3. Tag:

```bash
git tag v0.1.0
git push origin v0.1.0
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
