# CAPAS Physical Evidence Profile Registration Request Draft

Profile name: CAPAS Physical Evidence Profile

Draft profile URI:

```text
https://example.org/capas-inteligentes/ro-crate/physical-evidence/0.1
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
