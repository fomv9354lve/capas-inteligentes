# Public / Private Boundary

CAPAS public release assets contain the claim gate, evidence profile, validators,
CLI, UI, and a shipped evidence corpus.

They intentionally do not contain private/local scientific engines or adapters
used during exploratory corpus generation. In particular, the public package must
not delegate routing or execution to a private lab repository.

Public contract:

- inspect and decide claims over shipped traces;
- validate RO-Crate / PROV-shaped evidence artifacts;
- expose evidence fields such as `physical_evidence_level`,
  `verification_independence`, `evidenceStatus`, and `claim_scope`;
- keep `fine_tune_ready=False` until blind inference review exists.

Non-contract:

- full regeneration of all historical traces from private engines;
- private simulator routing frontiers;
- private hardware-specific optimization logic;
- external user validation;
- formal RO-Crate profile registration.

If public full-regeneration becomes a goal, CAPAS needs public engine adapters or
a declared public benchmark dependency. Until then, shipped traces are the public
audit artifact and private engines remain outside the release boundary.
