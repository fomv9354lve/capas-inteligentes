# CAPAS Physical Evidence Profile review request

Status: draft profile, local validation complete, not formally registered.

## Request

I would like feedback on whether the CAPAS Physical Evidence Profile should be
represented as:

1. a RO-Crate profile,
2. a Workflow Run RO-Crate sub-profile,
3. an application profile documented outside the registry,
4. or a smaller vocabulary extension.

## Profile summary

CAPAS aligns with RO-Crate / Workflow Run RO-Crate run metadata and adds one
domain-specific evidence entity:

```text
capas:PhysicalEvidence
```

The entity records scientific-result evidence fields that generic workflow
provenance does not normally make first-class:

- physical evidence level,
- witness independence,
- reference truth,
- absolute error or bound scope,
- evidence status for success / none / failed / rejected,
- local-oracle and universal-anchor outcomes when applicable.

## Non-claims

CAPAS does not claim to replace RO-Crate, PROV, Workflow Run RO-Crate,
Metamorphic Testing, or VVUQ. It is a domain profile for evidence-typed
scientific-computation claim gating.

## Included local artifacts

- `docs/profile/CAPAS_PHYSICAL_EVIDENCE_PROFILE.md`
- `docs/profile/capas-physical-evidence-context.jsonld`
- `docs/profile/capas-profile-registration.json`
- `docs/WORKFLOW_RUN_RO_CRATE_ALIGNMENT.md`
- `benchmarks/ro_crates/trace_039/ro-crate-metadata.json`
- `benchmarks/validate_capas_profile.py`

## Questions for reviewers

1. Is `capas:PhysicalEvidence` best modeled as a profile-specific entity, or
   should it be represented with existing Workflow Run RO-Crate terms?
2. Should evidence states such as `none_declared`, `not_applicable_failed`, and
   `not_applicable_rejected` be profile terms, action statuses, or both?
3. Which validator or competency checks should CAPAS pass before a profile
   registration request is considered meaningful?
4. Is this better submitted as a profile registry entry, a Workflow Run
   RO-Crate sub-profile, or an external application profile?

## Completion rule

This request does not make CAPAS registered. Formal registration is complete
only when an external registry, community process, or stable profile URI accepts
the profile.
