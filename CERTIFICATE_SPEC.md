# CAPAS verdict certificate: specification (v2, 2026-10-14)

This document is the only input a checker needs. A conforming checker reads a certificate, the rule table, and
optionally the payload, and accepts or rejects the certificate. It never imports or calls the CAPAS engine
(`capas.py`). PLAN_v3 A1 requires that the reference checker, `capas_check.py`, is written from this
document by a session that did not write the engine (GOVERNANCE §6: constructor ≠ verifier).

## 1. Inputs

**Rule table** (`docs/rule_table.json`). A JSON object with a `rules` array. Each rule has:

| field | meaning |
|---|---|
| `id` | rule id, unique within the table |
| `version` | integer |
| `stage` | `base`, `downgrade` or `annotate` |
| `claim_type` | a claim type string, or null (any type) |
| `verdict` | base rules only: the verdict the rule sets (`ACCEPT`, `REWRITE`, `REJECT`, `HOLD`) |
| `from` | downgrade rules: the list of verdicts the rule may act on; annotate rules: null |
| `to` | downgrade rules: the verdict after the rule; annotate rules: null (verdict unchanged) |
| `pattern` | a regular expression (Python `re` syntax) that must match one reason segment **in full** |
| `hold_class`, `label`, `giant`, `source` | informative; a checker may ignore them |

`rule_table_sha256` is `"sha256:"` followed by the lowercase hex SHA-256 of the table file's exact bytes.

**Certificate**: a JSON object, the decision the engine returned. The checker uses these fields:

| field | type |
|---|---|
| `schema_version` | string |
| `input_claim` | object with `id`, `type`, `text` (or the redacted form with `text_sha256`) |
| `verdict` | one of the four verdicts |
| `reason` | string |
| `required_fields` | array of strings |
| `invariant_audit` | object with a `verdict` string, or null / absent |
| `audit_hash_recipe` | must be `"v2"` |
| `engine_version` | string |
| `rule_table_sha256` | string |
| `rules_fired` | array of rule ids, in order |
| `evidence_sha256` | string |
| `notices` | array of strings (may be empty) |
| `audit_hash` | string |

**Sealed certificate** (a record of a sealed batch). An object `{certificate, seal, seal_hash}` where `seal` is
`{engine_tag, engine_commit, sealed_at, sealed_by, run_by}`, all strings, and `seal_hash` is defined in §4.

**Payload** (optional): the object the engine decided, with `evidence` (object) and optional `meta` (object).

## 2. Canonical JSON and hashing

`canon(x)` is the JSON serialization of `x` with object keys sorted, separators `,` and `:` (no spaces), non-ASCII
characters escaped as `\uXXXX` (the default of Python's `json.dumps`), and no trailing newline.
`H(x) = "sha256:" + hex(SHA-256(UTF-8(canon(x))))`.

## 3. Audit hash, recipe v2

```
body = {
  "schema_version":   certificate.schema_version,
  "input_claim":      certificate.input_claim,
  "verdict":          certificate.verdict,
  "reason":           certificate.reason,
  "required_fields":  certificate.required_fields, or [] if absent or null,
  "invariant_audit":  certificate.invariant_audit.verdict if invariant_audit is an object, else null,
  "audit_hash_recipe": "v2",
  "engine_version":   certificate.engine_version,
  "rule_table_sha256": certificate.rule_table_sha256,
  "rules_fired":      certificate.rules_fired,
  "evidence_sha256":  certificate.evidence_sha256,
  "notices":          certificate.notices, or [] if absent or null
}
audit_hash = H(body)
```

`evidence_sha256 = H({"evidence": E, "meta": M})` where `E` is `payload.evidence` when it is an object and `{}`
otherwise (absent, or any non-object value), and `M` is `payload.meta` as given (any JSON value), or null if absent.
(Clarified 2026-10-14 after the first checker run: a payload whose evidence is not an object is a schema-error HOLD,
and its evidence hashes as `{}`.)

## 4. Seal hash

`seal_hash = H({"audit_hash": certificate.audit_hash, "seal": seal})`.

## 5. Reason grammar

A reason is one **base segment** followed by zero or more **tail segments**, each tail segment preceded by the
two characters `"; "`. Tail segments come from `downgrade` or `annotate` rules. The separator `"; "` can also occur
inside a segment, so a reason does not split uniquely on `"; "`. The certificate's `rules_fired` fixes the
decomposition: segment *i* must full-match the pattern of `rules_fired[i]`, and the segments joined with `"; "`
must equal `reason` exactly. A checker therefore searches for split points such that every segment matches its
assigned rule. If any assignment of split points works, the decomposition holds.

## 6. Verdict replay

```
v = verdict of rules_fired[0]          (must be a base rule)
for each later rule r in rules_fired:
    r must be downgrade or annotate     (a second base rule is an error)
    if r is downgrade:
        v must be in r.from            (else error: rule acted outside its domain)
        v = r.to
final v must equal certificate.verdict
```

## 7. Checks, all required for acceptance

1. `audit_hash_recipe` is `"v2"`.
2. The supplied rule table's SHA-256 equals `rule_table_sha256`.
3. Every id in `rules_fired` exists in the table. The list is non-empty, and its first rule is a base rule.
4. The reason decomposes per §5.
5. The replay of §6 gives `certificate.verdict`.
6. The first rule's `claim_type` is null or equals `input_claim.type`.
7. Every downgrade or annotate rule's `claim_type` is null or equals `input_claim.type`.
8. The recomputed audit hash (§3) equals `audit_hash`.
9. If a payload is supplied, the recomputed `evidence_sha256` equals the certificate's value.
10. For a sealed certificate, the recomputed `seal_hash` equals `seal_hash`, and every `seal` field is a non-empty string.

The checker reports, per certificate, `ACCEPTED` or `REJECTED` with the numbers of the checks that failed. It never
repairs a certificate.

## 8. What acceptance means

An accepted certificate shows four things:
- The verdict follows from the published rule table and the reason it carries.
- The reason is composed only of published rules.
- The record has not changed since it was hashed, and, for a sealed certificate, since it was sealed.
- The evidence hash matches the payload, when the payload is supplied.

Seal fields are exactly the five listed in §1; a seal with other fields fails check 10. A malformed certificate
(wrong field types) is rejected and reported as check 0; a malformed rule table (duplicate ids, a pattern that
does not compile, a bad stage or verdict) fails check 3 for every record. Rule versions are covered by the table hash (check 2).

It does **not** show that the engine evaluated each rule's condition correctly on the evidence. That needs the
engine, or a second implementation of each rule's predicate. It also does not show that the declared evidence is
true (the GIGO ceiling).
