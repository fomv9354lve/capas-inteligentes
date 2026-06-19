# CAPAS Security and Compliance Appendix

## Security posture

- Deterministic decision logic; no LLM judge in the gate.
- CSP-hardened static UI with no external runtime dependencies.
- Optional bearer token for the local API.
- Workspace-scoped JSONL audit log for API decisions.
- Schema versioning fails closed for missing or old payload versions.
- Payload angle-bracket guards reduce downstream XSS risk.
- Sensitive mode can redact payload sharing in the browser.

## Compliance mapping

CAPAS supports evidence governance controls that are relevant to regulated AI
programs:

- training-data provenance documentation
- human review traceability
- source hash verification
- schema-controlled data contracts
- audit export for decision trails
- fine-tune readiness blockers before training

CAPAS does not certify broad scientific truth. It gates supplied evidence
fields against deterministic criteria and records why a claim is accepted,
rewritten, rejected, or held.
