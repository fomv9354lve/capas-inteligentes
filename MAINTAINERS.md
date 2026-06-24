# Maintainers, roles & access

Documented for transparency (OpenSSF Baseline GV-01.01 access list, GV-01.02 roles & responsibilities).

## Maintainers

| Name | GitHub | Role | Responsibilities |
|------|--------|------|------------------|
| Fco. Osvaldo Morales Vilchis | [@fomv9354lve](https://github.com/fomv9354lve) | Lead maintainer | Code review & merge, releases, security response, dependency review, governance. |

## Access to sensitive resources

| Resource | Who has access | How |
|----------|----------------|-----|
| GitHub repository (admin) | @fomv9354lve | account 2FA |
| PyPI project `capas-claim-gate` | GitHub Actions, release-triggered only | OIDC Trusted Publishing — no long-lived token |
| Signing / provenance | none stored | Sigstore keyless (OIDC); no private keys at rest |

## Honest scope — bus factor

The project currently has **one** maintainer (**bus factor = 1**). OpenSSF Best Practices (Silver/Gold) and
Baseline criteria that require **two independent maintainers** — `bus_factor ≥ 2`, two-person review,
contributors-unassociated — are **not met and are not claimed**. Adding a second independent maintainer is an
open governance item tracked in [ROADMAP.md](ROADMAP.md); the certification-mark/escrow governance is in
[GOVERNANCE.md](GOVERNANCE.md).

## Continuity

Repository admin and PyPI publishing are bound to the maintainer's GitHub account (2FA + OIDC Trusted
Publishing, no stored secrets). A documented continuity plan (recovery access, a second credential holder) is
an open item in the roadmap — disclosed rather than implied.

## Reporting & decisions

- Security: see [SECURITY.md](SECURITY.md) (private reporting + coordinated disclosure window).
- Contributions & review process: see [CONTRIBUTING.md](CONTRIBUTING.md).
- Conduct: see [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
