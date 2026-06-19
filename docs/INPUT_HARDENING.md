# CAPAS Input Hardening Notes

Status: public claim-gate input hardening after external adversarial review.

## Fixed Critical Issues

The external `exact_model_solution` rule compares `abs_error <= tolerance`.
Because both fields are supplied by external input, the gate now validates:

- `abs_error` must be numeric, finite, and `>= 0`.
- `tolerance` must be numeric, finite, and `>= 0`.
- booleans are rejected as numeric values in Python, even though `bool` is a
  subclass of `int`.

This prevents payloads such as:

```json
{"abs_error": -999, "tolerance": 0.01}
```

or:

```json
{"abs_error": -5, "tolerance": -1}
```

from licensing an `ACCEPT`. They now produce `HOLD` with schema errors.

## Exact Zero Tolerance

`tolerance = 0` remains valid by design. It means an exact equality check:

- `abs_error = 0`, `tolerance = 0` -> `ACCEPT`
- `abs_error > 0`, `tolerance = 0` -> `REJECT`

This is intentionally strict, not a default recommendation for noisy scientific
measurements.

## Length Limits

The external payload validator now applies:

- `claim.id <= 256`
- `claim.text <= 2000`
- `evidence.current_claim <= 4000`

The goal is not semantic censorship. It is to keep the static demo and simple
CLI payload surface from accepting unbounded strings.

## Downstream Rewrite Safety

`current_claim` can flow into `rewrite` and `licensed_claim` for
`claim_transition` when stronger upgrade evidence is absent. The CAPAS UI escapes
HTML before rendering, but downstream consumers may not.

Therefore `evidence.current_claim` rejects raw `<` and `>` angle brackets.

This is a conservative product-boundary rule for the public MVP. If a future API
needs mathematical inequalities in `current_claim`, it should carry structured
math fields rather than raw HTML-like text.

## Unknown Evidence

For required fields, the value `"unknown"` is treated like missing evidence.
Example:

```json
{"anchor_mode": "unknown"}
```

does not mean "some other anchor." It means the anchor was not declared strongly
enough to license an `absolute_anchor` claim, so the decision is `HOLD`.

## Regression Coverage

The hardening is covered by `benchmarks/verify_external_input_schema.py`:

- negative `abs_error`
- negative `tolerance`
- double-negative exploit
- boolean-as-number exploit
- oversized `claim.id`
- raw HTML in `current_claim`
- exact zero-tolerance semantics
- `"unknown"` as missing required evidence
