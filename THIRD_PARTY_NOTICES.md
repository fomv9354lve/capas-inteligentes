# Third-Party Notices

CAPAS (`capas-claim-gate`) is licensed under Apache-2.0. The deterministic core imports only **numpy**
from third parties; everything else is optional or a dev/build tool. No GPL/AGPL code is used or
redistributed, and no proprietary code is embedded. This file records the third-party components and
their licenses, as required by their terms and for enterprise procurement review.

## Redistributed with the product

| Component | Where | License | Notes |
|---|---|---|---|
| **numpy** | core runtime dependency | BSD-3-Clause | the only hard third-party dependency of the engine |
| **three.js** (r128) | `docs/vendor/three-r128/` — served on the site (3D logo) | MIT | © three.js authors; the MIT notice is retained in the minified file header |

## Build / dev / example tools (NOT shipped in the `capas-claim-gate` package)

| Component | Where | License | Notes |
|---|---|---|---|
| **axe-core** | `designlab/vendor/axe.min.js` | MPL-2.0 | © Deque Systems; local accessibility checker; excluded from the container build (`.dockerignore`) |
| **qiskit**, **qiskit-aer** | `examples/`, `benchmarks/verify_xeb_purity.py` | Apache-2.0 | IBM's own libraries; used to run/audit IBM Quantum devices and to build the calibrated noise model. Not a core dependency and not redistributed in the package. |

## Optional extras (`[project.optional-dependencies]`, installed only on request)

scipy (BSD-3-Clause) · stim (Apache-2.0) · pyscf (Apache-2.0) · quimb (BSD-3-Clause) · **cotengra (Apache-2.0)** ·
**ro-crate / rocrate (Apache-2.0)** · pypdf (BSD-3-Clause). All are permissive (BSD / MIT / Apache-2.0);
cotengra and ro-crate were confirmed Apache-2.0 from installed package metadata (2026-06-24).
*Maintainer note: rocrate-validator was not installed at audit time — confirm its exact SPDX identifier
(believed Apache-2.0) before tagging a public release.*

## IBM Quantum results

Results attributed to `ibm_kingston` (e.g. `benchmarks/kingston_real_bell_verdict.json`,
`examples/kingston_live_audit.py`) are measurements we ran on IBM Quantum hardware under the open plan,
plus IBM's own published calibration ("atlas") values used as a comparison oracle. IBM Quantum permits
publication of results obtained on its systems. References to "IBM", device names, and published
calibration values are nominative fair use for comparison and **do not imply IBM's endorsement,
sponsorship, or partnership** — see the consilience scope note on the site and in
`docs/capas_vs_sota_and_ibm.md`.

## Marks

"CAPAS" and the CAPAS certification mark are reserved (see `NOTICE` and `GOVERNANCE.md`). Third-party
names and marks (IBM, Qiskit, Pinnacle 21, etc.) are the property of their respective owners and are used
only nominatively.

*This notice is informational and not legal advice; verify SPDX identifiers at release time.*
