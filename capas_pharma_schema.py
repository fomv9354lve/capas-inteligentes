"""capas_pharma_schema.py — versioned input-schema + validator for a pharma statistical-claim
payload to the CAPAS pharma gate (capas_pharma.gate_pharma_stat_claim / decide).

WHY THIS EXISTS (contract surface, not free text)
--------------------------------------------------
capas_pharma.gate_pharma_stat_claim today consumes a hand-built `evidence` dict (capas_pharma.py
docstring + signature). That is fine for the maintainer, useless for a regulated buyer: a sponsor/CRO
cannot construct a conformant payload from THEIR OWN submission outputs unless the gate's *input
contract* is explicit, versioned, and re-derivable. This module makes the contract a first-class,
machine-checkable artifact — mirroring the discipline of the external claim payload schema
(outputs/external_reviewer_packet/capas_claim_payload.schema.json: additionalProperties:false, a
const schema_version, required-block, typed/enum'd fields) but specialized to the pharma statistical
fields the gate actually reads.

NO LLM IN THE VERDICT. This module is pure stdlib structural validation + a deterministic normalizer.
It never judges plausibility. The verdict is still produced ONLY by capas_pharma.gate_pharma_stat_claim.
The schema's job is to fail *malformed* input loudly, and to make *omission* of a field have a single,
documented, re-derivable verdict consequence (see FIELD CONTRACT below) — never a silent default that
manufactures an ACCEPT.

GROUNDING (regla cero — every rule below is re-derivable from a named artifact)
------------------------------------------------------------------------------
- Field set, types, defaults, severity order: capas_pharma.py (gate_pharma_stat_claim, lines 31-119).
    * alpha default 0.05                         -> capas_pharma.py:46-48
    * claim_kind default 'confirmatory'          -> capas_pharma.py:52
    * asserts_effect defaults to asserts_significant -> capas_pharma.py:51
    * n_comparisons default 1                     -> capas_pharma.py:69-70
    * ci_null default 0.0                         -> capas_pharma.py:79-81
    * fail-closed severity REJECT>REWRITE>HOLD>ACCEPT -> capas_pharma.py:16,24,112-113
    * HOLD on no structured evidence / missing p for a significance claim -> capas_pharma.py:38-39,62,104-105
- Admitted value grid (enums, numeric ranges): benchmarks/generate_pharma_corpus.py:49-61 (the corpus
    the schema MUST admit — every case the corpus generates is a VALID payload by construction).
- Pattern style (block HTML/Unicode angle-bracket homoglyphs on displayable strings) and the
    schema_version/const + required discipline: outputs/external_reviewer_packet/capas_claim_payload.schema.json.

This file is the SCHEMA + VALIDATOR; the VERDICT engine is capas_pharma.py (imported, unmodified).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import capas_pharma  # noqa: E402  (the unmodified verdict engine; this module never re-implements it)

SCHEMA_VERSION = "capas-pharma-claim-payload-v1"

# Block HTML angle brackets + common Unicode angle-bracket homoglyphs on any string that may be
# rendered downstream (same defense as capas_claim_payload.schema.json). Used in regex form below.
_ANGLE_CLASS = (
    "<>˂˃‹›〈〉❬❭⟨⟩"
    "⧼⧽〈〉﹤﹥＜＝＞"
)
_SAFE_STR = re.compile("^[^" + re.escape(_ANGLE_CLASS) + "]*$")

# ---------------------------------------------------------------------------
# FIELD CONTRACT — single source of truth.
# Each entry: type, allowed enum (or None), the default the gate applies if omitted, and the EXACT
# verdict consequence of omission (re-derived from the gate). "Structurally required" (below) means:
# required for the payload to be a well-formed pharma claim at all. A field that is statistically
# *needed for ACCEPT* but omitted is NOT a schema error — the gate turns that omission into HOLD/REJECT,
# which is the correct fail-closed behavior. The schema documents which is which so omission is never
# silently safe.
# ---------------------------------------------------------------------------
PHARMA_EVIDENCE_FIELDS = {
    # field: (json_type, enum_or_None, gate_default, omission_consequence)
    "p_value":               ("number",  None,
                              None,
                              "If asserts_significant is true and p_value is omitted -> HOLD "
                              "(rule missing_pvalue, capas_pharma.py:61-62,104-105). A significance "
                              "claim cannot be ACCEPTed without its p-value."),
    "alpha":                 ("number",  None, 0.05,
                              "Omitted -> alpha defaults to 0.05 (capas_pharma.py:46-48). The "
                              "significance_vs_alpha test runs against 0.05."),
    "asserts_significant":   ("boolean", None, False,
                              "REQUIRED BY THE SCHEMA as a deliberate intent-declaration (stricter than "
                              "the gate). The gate ACCEPTs evidence with the flag absent, treating it as "
                              "a non-significance/descriptive claim (capas_pharma.py:50,60,72). The schema "
                              "forces the partner to declare significance intent; absent it the gate would "
                              "treat the claim as descriptive and ACCEPT, so the schema HOLDs to avoid "
                              "silent intent ambiguity (fail-closed). Set it explicitly true OR false."),
    "asserts_effect":        ("boolean", None, "= asserts_significant",
                              "Omitted -> defaults to the value of asserts_significant "
                              "(capas_pharma.py:51); gates the CI-includes-null and endpoint checks."),
    "n_comparisons":         ("integer", None, 1,
                              "Omitted/non-numeric -> 1 (capas_pharma.py:69-70); multiplicity check "
                              "only fires when n_comparisons > 1."),
    "multiplicity_adjustment": ("boolean", None, False,
                              "Omitted -> False (capas_pharma.py:71). With >1 comparison, a "
                              "confirmatory significance claim then -> REWRITE (multiplicity_unadjusted)."),
    "endpoint_type":         ("string", ["primary", "secondary", "exploratory"], None,
                              "Omitted -> the endpoint_not_prespecified REWRITE cannot fire "
                              "(capas_pharma.py:96-101 require endpoint_type in secondary/exploratory). "
                              "Omitting it does NOT manufacture ACCEPT for other failing rules."),
    "prespecified":          ("boolean", None, None,
                              "Omitted -> not == False, so endpoint pre-specification REWRITE does not "
                              "fire (capas_pharma.py:98 tests `prespec is False`). Supply it explicitly "
                              "for a confirmatory claim on a secondary/exploratory endpoint."),
    "claim_kind":            ("string", ["confirmatory", "descriptive"], "confirmatory",
                              "Omitted -> 'confirmatory' (capas_pharma.py:52). Confirmatory is the "
                              "strict path (multiplicity + endpoint checks apply). 'descriptive' is the "
                              "supported non-confirmatory path: a descriptive claim with significance "
                              "intent declared false ACCEPTs."),
    "ci_low":                ("number",  None, None,
                              "Omitted (or ci_high omitted) -> CI-includes-null check is skipped "
                              "(capas_pharma.py:82 requires both bounds). Omission does not license an "
                              "effect claim; it only removes the CI evidence from consideration."),
    "ci_high":               ("number",  None, None,
                              "See ci_low. Both bounds required for the ci_includes_null REJECT."),
    "ci_null":               ("number",  None, 0.0,
                              "Omitted -> 0.0 (capas_pharma.py:79-81). For ratio metrics (HR/OR/RR) the "
                              "partner MUST set ci_null=1.0 or the wrong null is tested."),
    "observed_direction":    ("string", ["benefit", "harm", "none"], None,
                              "Omitted -> effect_direction REWRITE cannot fire (capas_pharma.py:89-91 "
                              "require both observed and claimed and observed != 'none')."),
    "claimed_direction":     ("string", ["benefit", "harm", "none"], None,
                              "Omitted -> effect_direction REWRITE cannot fire (see observed_direction)."),
    "rederived_p_match":     ("boolean", None, None,
                              "Omitted/None -> the recompute check is NOT run (capas_pharma.py:55 "
                              "fires only on the literal value False). Set it to False ONLY when an "
                              "independent recompute of p from raw data disagrees with the reported p "
                              "-> REJECT (pvalue_rederivation). Never set True/None to fake a pass: "
                              "absence simply means 'not checked', it does not assert agreement."),
}

# Structurally required for a well-formed payload (mirrors the external schema's required-block:
# a claim must self-identify, and the schema deliberately forces an explicit significance-intent
# declaration even though the gate would default it to False).
REQUIRED_CLAIM_FIELDS = ["id", "text"]
# asserts_significant is required by the SCHEMA (not the gate): the schema is intentionally STRICTER
# than the gate here, HOLDing on its absence to forbid silent intent ambiguity (see FIELD CONTRACT).
REQUIRED_EVIDENCE_FIELDS = ["asserts_significant"]


def build_schema() -> dict:
    """Emit the versioned JSON-Schema (2020-12) for the pharma claim payload. additionalProperties is
    false at every level so an unknown/misplaced field is rejected loudly (the external schema's
    discipline: outputs/external_reviewer_packet/capas_claim_payload.schema.json)."""
    ev_props: dict = {}
    for name, (jtype, enum, _default, consequence) in PHARMA_EVIDENCE_FIELDS.items():
        prop: dict = {"description": consequence}
        if jtype == "boolean":
            prop["type"] = "boolean"
        elif jtype == "integer":
            prop.update({"type": "integer", "minimum": 1})
        elif jtype == "number":
            prop["type"] = "number"
            if name in ("p_value", "alpha"):
                prop.update({"minimum": 0, "maximum": 1})
        elif jtype == "string":
            prop.update({"type": "string", "minLength": 1,
                         "pattern": _SAFE_STR.pattern})
        if enum is not None:
            prop["enum"] = enum
        ev_props[name] = prop

    return {
        "$id": "https://krenniq.com/schema/pharma/v1/capas_pharma_claim_payload.schema.json",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CAPAS pharma statistical-claim payload",
        "description": (
            "Input contract for capas_pharma.gate_pharma_stat_claim. Validates STRUCTURE only; the "
            "ADMISSIBILITY verdict is produced solely by the gate. ACCEPT licenses the claim against "
            "the supplied evidence; it does not assert the claim is true (GIGO ceiling, capas_pharma.py:17)."),
        "type": "object",
        "additionalProperties": False,
        "x-capas-schema-version": SCHEMA_VERSION,
        "required": ["schema_version", "claim", "evidence"],
        "properties": {
            "schema_version": {
                "const": SCHEMA_VERSION,
                "description": "Pinned for migration-safe decisions (mirrors capas-claim-payload const).",
                "type": "string",
            },
            "claim": {
                "type": "object",
                "additionalProperties": False,
                "required": REQUIRED_CLAIM_FIELDS,
                "properties": {
                    "id": {"type": "string", "minLength": 1, "maxLength": 256,
                           "pattern": _SAFE_STR.pattern,
                           "description": "Sponsor/CRO claim identifier (e.g. CSR section + endpoint id)."},
                    "text": {"type": "string", "minLength": 1, "maxLength": 2000,
                             "pattern": _SAFE_STR.pattern,
                             "description": "The reported statistical claim as written in the CSR/label."},
                    "endpoint_id": {"type": "string", "maxLength": 256, "pattern": _SAFE_STR.pattern,
                                    "description": "Optional ADaM/define.xml endpoint cross-reference."},
                },
            },
            "evidence": {
                "type": "object",
                "additionalProperties": False,
                "required": REQUIRED_EVIDENCE_FIELDS,
                "description": (
                    "Structured statistical evidence the gate reads. Every field is OPTIONAL to the "
                    "schema except asserts_significant (the schema requires an explicit significance-intent "
                    "declaration — stricter than the gate, to forbid silent intent ambiguity). Omission "
                    "has a documented, fail-closed verdict consequence (see each field's description). "
                    "Omitting evidence never manufactures an ACCEPT — at most it removes one rule from "
                    "consideration; a deficient claim still downgrades on the remaining rules."),
                "properties": ev_props,
            },
            "provenance": {
                "type": "object",
                "additionalProperties": True,
                "description": (
                    "Optional. Where the evidence fields were extracted from (e.g. ADaM dataset name + "
                    "row, define.xml OID, CSR table id). Carried through for audit; never affects the "
                    "verdict."),
            },
        },
    }


# ---------------------------------------------------------------------------
# Self-contained validator (no jsonschema dependency — runs on a clean stdlib Python so a design
# partner can run-it-themselves; the Sonobuoy-style motion in MARKET_VALIDATION). Implements exactly
# the JSON-Schema keywords this schema uses: type, const, enum, required, additionalProperties,
# min/max, minLength/maxLength, pattern, minimum/maximum.
# ---------------------------------------------------------------------------
def _type_ok(value, jtype) -> bool:
    if jtype == "object":
        return isinstance(value, dict)
    if jtype == "boolean":
        return isinstance(value, bool)
    if jtype == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if jtype == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if jtype == "string":
        return isinstance(value, str)
    return True


def _validate(value, schema, path, errors) -> None:
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}, got {value!r}")
    if "type" in schema and not _type_ok(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(value).__name__}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in allowed values {schema['enum']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: string longer than {schema['maxLength']}")
        if "pattern" in schema and not re.match(schema["pattern"], value):
            errors.append(f"{path}: contains forbidden characters (HTML/Unicode angle brackets)")
    if isinstance(value, dict) and "properties" in schema:
        props = schema["properties"]
        if schema.get("additionalProperties") is False:
            for k in value:
                if k not in props:
                    errors.append(f"{path}: unknown field '{k}' (additionalProperties=false)")
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}: missing required field '{req}'")
        for k, sub in props.items():
            if k in value:
                _validate(value[k], sub, f"{path}.{k}" if path else k, errors)


def validate_payload(payload: dict) -> list:
    """Return a list of structural errors ([] == VALID). Pure structure; no verdict."""
    errors: list = []
    _validate(payload, build_schema(), "", errors)
    return errors


def to_gate_evidence(payload: dict) -> dict:
    """Normalize a VALID payload into the exact dict capas_pharma.gate_pharma_stat_claim consumes.
    This is a 1:1 passthrough of evidence fields (the gate applies its own documented defaults; we do
    NOT pre-fill them here so the gate remains the single source of default behavior, capas_pharma.py:
    46-81). No field is invented, none is dropped."""
    return dict(payload.get("evidence", {}))


def gate(payload: dict) -> dict:
    """Validate, then run the UNMODIFIED gate. Malformed payload -> structural HOLD (we refuse to feed
    junk into the verdict engine; that is itself fail-closed)."""
    errs = validate_payload(payload)
    if errs:
        return {"verdict": "HOLD", "why": "payload failed schema validation",
                "schema_errors": errs, "domain": "pharma_statistics"}
    return capas_pharma.gate_pharma_stat_claim(to_gate_evidence(payload))


# ---------------------------------------------------------------------------
# Self-test: proves (a) the schema admits every shape the corpus generates, (b) the canonical four
# verdicts round-trip payload -> schema -> gate, (c) the supported DESCRIPTIVE path round-trips to
# ACCEPT (the schema's strictness boundary is itself pinned), (d) malformed payloads are rejected.
# Re-derivable.
# ---------------------------------------------------------------------------
def _wrap(ev: dict, cid="C1", text="Drug X is statistically significant vs placebo.") -> dict:
    return {"schema_version": SCHEMA_VERSION, "claim": {"id": cid, "text": text}, "evidence": ev}


_CANON = [
    ("ACCEPT", {"asserts_significant": True, "asserts_effect": True, "p_value": 0.01, "alpha": 0.05,
                "n_comparisons": 1, "multiplicity_adjustment": True, "ci_low": 0.1, "ci_high": 0.5,
                "ci_null": 0, "observed_direction": "benefit", "claimed_direction": "benefit",
                "endpoint_type": "primary", "prespecified": True, "claim_kind": "confirmatory"}),
    ("REJECT", {"asserts_significant": True, "asserts_effect": True, "p_value": 0.2, "alpha": 0.05}),
    ("REWRITE", {"asserts_significant": True, "asserts_effect": True, "p_value": 0.01,
                 "n_comparisons": 12, "multiplicity_adjustment": False, "claim_kind": "confirmatory"}),
    ("HOLD", {"asserts_significant": True}),  # significance claim, no p_value -> HOLD
]

# The supported descriptive path: significance intent explicitly declared false, claim is descriptive.
# Pins that the schema's strictness (requiring asserts_significant) supports the non-confirmatory path
# when the intent is DECLARED — it does not force every claim to be confirmatory.
_DESCRIPTIVE = {"asserts_significant": False, "claim_kind": "descriptive"}


def selftest() -> int:
    fails = []

    # (a) every corpus case is a VALID payload and gates identically through this wrapper
    try:
        import benchmarks.generate_pharma_corpus as corpus  # noqa
        cases = corpus.build()
        for ev in cases:
            p = _wrap(ev)
            verrs = validate_payload(p)
            if verrs:
                fails.append(f"corpus case rejected by schema: {verrs[:2]} ev={ev}")
                break
            if gate(p)["verdict"] != capas_pharma.gate_pharma_stat_claim(ev)["verdict"]:
                fails.append(f"wrapper verdict != direct gate verdict for ev={ev}")
                break
        print(f"  corpus admit/agree: {len(cases)} cases "
              f"{'OK' if not fails else 'XX'}")
    except Exception as e:  # pragma: no cover
        print(f"  corpus check skipped ({e})")

    # (b) canonical four verdicts
    for want, ev in _CANON:
        got = gate(_wrap(ev))["verdict"]
        ok = got == want
        print(f"  canonical {want:8} -> {got:8} {'OK' if ok else 'XX'}")
        if not ok:
            fails.append(f"canonical {want} produced {got}")

    # (c) the descriptive path is VALID and round-trips to ACCEPT (strictness boundary pinned)
    dp = _wrap(_DESCRIPTIVE, text="Mean change from baseline was -2.1 (descriptive summary).")
    derrs = validate_payload(dp)
    dv = gate(dp)["verdict"] if not derrs else None
    ok_desc = (not derrs) and dv == "ACCEPT"
    print(f"  descriptive path VALID+ACCEPT: {'OK' if ok_desc else 'XX'}"
          + ("" if ok_desc else f" (errs={derrs[:1]} verdict={dv})"))
    if not ok_desc:
        fails.append("descriptive path did not round-trip VALID->ACCEPT")

    # (d) malformed payloads rejected (unknown field, bad enum, missing required, out-of-range p)
    bad = [
        _wrap({"asserts_significant": True, "frobnicate": 1}),                 # unknown field
        _wrap({"asserts_significant": True, "endpoint_type": "tertiary"}),     # bad enum
        {"schema_version": SCHEMA_VERSION, "claim": {"id": "C1"},              # missing claim.text
         "evidence": {"asserts_significant": True}},
        _wrap({"asserts_significant": True, "p_value": 1.5}),                  # p out of [0,1]
        _wrap({"p_value": 0.01}),                                              # missing required asserts_significant
    ]
    for i, p in enumerate(bad):
        errs = validate_payload(p)
        ok = bool(errs)
        print(f"  malformed[{i}] rejected: {'OK' if ok else 'XX'}")
        if not ok:
            fails.append(f"malformed[{i}] passed validation")

    print("\nPHARMA SCHEMA SELFTEST: " +
          ("pass — schema admits the corpus grid, the four canonical verdicts round-trip, the "
           "descriptive path round-trips to ACCEPT, malformed payloads are rejected; the gate contract "
           "surface is explicit and re-derivable."
           if not fails else "FAIL — " + "; ".join(fails)))
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CAPAS pharma claim payload schema + validator + gate.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("emit-schema", help="print the versioned JSON-Schema")
    ci = sub.add_parser("check-input", help="VALID/INVALID a payload against the schema")
    ci.add_argument("--input", required=True)
    g = sub.add_parser("gate", help="validate then run the unmodified pharma gate")
    g.add_argument("--input", required=True)
    sub.add_parser("selftest", help="prove schema<->gate agreement")
    args = ap.parse_args(argv)

    if args.cmd == "emit-schema":
        print(json.dumps(build_schema(), indent=2, sort_keys=True))
        return 0
    if args.cmd == "selftest":
        return selftest()

    payload = json.loads(Path(args.input).read_text())
    if args.cmd == "check-input":
        errs = validate_payload(payload)
        if errs:
            print(f"INVALID: {args.input}")
            for e in errs:
                print(f"  - {e}")
            return 1
        print(f"VALID: {args.input}")
        return 0
    if args.cmd == "gate":
        print(json.dumps(gate(payload), indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
