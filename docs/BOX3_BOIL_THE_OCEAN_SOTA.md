# Box 3 Boil-the-Ocean SotA Audit

Date: 2026-06-17

Purpose: hostile audit of the ten "we do not know that we know" intuitions
behind CAPAS. This document tries to kill broad claims first, then records the
narrow version that survives.

## Sources Checked

Primary neighbors found in this pass:

- "From Agent Traces to Trust: Evidence Tracing and Execution Provenance in LLM
  Agents" (arXiv:2606.04990)
- "ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM
  Agents" (arXiv:2606.18037)
- "PaperTrail: A Claim-Evidence Interface for Grounding Provenance in LLM-based
  Scholarly Q&A" (arXiv:2602.21045)
- "TraceSafe: A Systematic Assessment of LLM Guardrails on Multi-Step
  Tool-Calling Trajectories" (arXiv:2604.07223)
- "TRACE: Toulmin-based Reasoning Assessment through Constructive Elements for
  LLM CoT Evaluation" (arXiv:2605.29656)
- "Recording provenance of workflow runs with RO-Crate" (arXiv:2312.07852)
- "PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in
  Agentic Workflows" (arXiv:2508.02866)
- FAIR Data Pipeline (arXiv:2110.07117)
- Nanopublications literature
- Toulmin/argumentation theory
- hierarchy of evidence / GRADE-style evidence grading
- physical quantities / dimensional analysis / International System of
  Quantities

## Verdict Summary

The broad world is taken:

- agent traces
- evidence tracing
- claim-level provenance
- source-aware factuality
- scholarly claim/evidence interfaces
- workflow provenance
- nanopublication-style atomic claims
- argument structure evaluation
- evidence hierarchies

The surviving CAPAS position is narrower:

```text
CAPAS is an evidence type system for scientific computation traces:
it assigns typed physical/computational evidence to a result and rejects claims
that exceed that evidence.
```

The differentiator is not "claims + evidence". That is taken.

The differentiator is:

```text
claim licensing over computation-native physical evidence:
solver/model/reference error, formal-bound scope, witness independence,
universal-law anchors, degeneracy, route failure, and no-evidence states.
```

## Ten-Point Audit

### 1. CAPAS as anti-semantic-collapse

Intuition:

CAPAS prevents distinct meanings of "verified" from collapsing into one word.

Hostile SotA:

This is adjacent to argumentation theory, Toulmin's claim/ground/warrant model,
scientific claim verification, evidence hierarchies, PaperTrail, and
ProvenanceGuard. Broad "prevent unsupported claims" is taken.

What survives:

CAPAS prevents a narrower collapse: computational scientific evidence types.

Examples:

- exact model solve != physical accuracy
- same-runtime certificate != independent witness
- local formal bound != global observable bound
- local property pass != universal scaling-law pass

Claim allowed:

```text
CAPAS rejects selected scientific overclaims when trace evidence does not license
them.
```

Claim not allowed:

```text
CAPAS solves semantic overclaiming in general.
```

Minimum test:

`benchmarks/validate_evidence_claims.py` must reject overclaims from existing
traces.

Current status:

covered, 9/9 checks passed.

### 2. Trace value as permission / claim licensing

Intuition:

The trace is not the point; the permission set it grants is the point.

Hostile SotA:

ProvenanceGuard decomposes answers into claims and checks source-specific
support. PaperTrail maps claims to evidence in scholarly QA. The 2026 agent
provenance survey names claim-level and semantic provenance as central open
directions. Broad "claim licensing" is taken.

What survives:

CAPAS licenses claims from computation-native evidence, not from text-source
support alone.

Examples:

- `trace_021` licenses "exact for STO-3G model", not "physically accurate H2".
- `trace_020` licenses "verified optimum set", not "unique decision".
- `trace_038` licenses "universal anchor caught violation", not "local tests
  are enough".

Claim allowed:

```text
CAPAS implements a first rule-based claim checker over physical evidence fields.
```

Claim not allowed:

```text
CAPAS is the first claim-evidence system for agents.
```

Minimum test:

Every allowed/rejected claim should cite the exact trace fields that license or
block it.

Current status:

covered in first checker; needs more claim classes.

### 3. Failures as boundary data

Intuition:

Failures are not junk; they identify the boundary hit by the computation.

Hostile SotA:

Agent trace/provenance work already treats failures as traceable events for
debugging, recovery, and observability. TraceSafe studies risks in intermediate
tool trajectories. Workflow systems also record failed executions.

What survives:

CAPAS gives scientific boundary names to failures:

- backend/environment boundary
- routing/cost boundary
- no-evidence boundary
- physical-law boundary
- model/reference boundary
- degeneracy/decision boundary

Claim allowed:

```text
CAPAS records scientific failure/rejection/no-evidence states as evidence-typed
boundary events.
```

Claim not allowed:

```text
CAPAS invents failure provenance.
```

Minimum test:

The corpus must include success, failure, rejection, no-evidence, and law-anchor
failure states under the same trace schema.

Current status:

covered.

### 4. Evidence geometry

Intuition:

Evidence is not a line from weak to strong; it is a coordinate system.

Hostile SotA:

Evidence hierarchies, GRADE, VVUQ, Toulmin qualifiers, provenance quality, and
argumentation frameworks already grade evidence or confidence. Broad "evidence
levels" are taken.

What survives:

CAPAS has a domain-specific evidence geometry:

```text
level: analytic / formal / experimental / estimated / none / scaling_law_anchor
independence: no_solver / different_method / same_runtime / none
scope: local / multi-step / model / physical / observable
status: success / failed / rejected / no_anchor
ambiguity: unique / degenerate / underdetermined
```

Claim allowed:

```text
CAPAS encodes a multidimensional evidence type for scientific computation
results.
```

Claim not allowed:

```text
CAPAS invents evidence grading.
```

Minimum test:

The checker must use at least two axes at once, e.g. evidence level plus scope,
or evidence level plus witness independence.

Current status:

partially covered; current checker uses evidence level, scope, degeneracy,
robustness, and anchor status. It does not yet reason deeply over independence.

### 5. Evidence algebra

Intuition:

The project is already using rules such as "formal local bound does not compose
to global bound" and "experimental distance does not imply accuracy".

Hostile SotA:

Argumentation frameworks, logic of argumentation, Toulmin warrants, GSN/safety
cases, evidence hierarchies, and VVUQ already provide ways to reason from
evidence to claims. Broad "evidence algebra" is taken.

What survives:

CAPAS can provide a small, executable algebra for scientific-computation trace
fields.

Seed rules:

- `exact_model_solution` can be accepted while `physical_accuracy` is rejected.
- `formal_bound` plus `single_bipartition_state_truncation` rejects global DMRG
  claims.
- `degeneracy_count > 1` rejects unique-decision claims.
- `local_property_tests_pass` does not imply universal-law satisfaction.

Claim allowed:

```text
CAPAS has an executable seed algebra mapping trace evidence types to allowed
claims.
```

Claim not allowed:

```text
CAPAS has a complete formal logic of scientific evidence.
```

Minimum test:

Add more rules and ensure no rule is based on fluent prose alone.

Current status:

seed implemented.

### 6. CAPAS as a claim compiler

Intuition:

CAPAS could generate the strongest safe sentence a result is allowed to say.

Hostile SotA:

Controlled natural language, nanopublications, semantic publishing, and
Toulmin-style argument reconstruction all address structured claims. Broad
"machine-readable scientific claims" is taken.

What survives:

CAPAS can compile safe scientific-computation claims from trace evidence.

Example:

```text
Input: solver_error=0, model_error=0.040, experimental evidence present
Safe output: "The declared model was solved exactly, but the model is outside
chemical accuracy against the measured reference."
Unsafe output: "The molecule is physically accurate."
```

Claim allowed:

```text
CAPAS can become a claim compiler for evidence-typed scientific computation
results.
```

Claim not allowed:

```text
CAPAS is a general semantic publishing system.
```

Minimum test:

Generate allowed natural-language claims from the same rules used by
`validate_evidence_claims.py`.

Current status:

not implemented.

### 7. Claim safety for scientific agents

Intuition:

CAPAS protects scientific agents from making stronger claims than their evidence
supports.

Hostile SotA:

TraceSafe, ProvenanceGuard, PaperTrail, TRACE, and the agent-provenance survey
all occupy nearby "agent trace / claim support / guardrail" space. Broad agent
claim safety is taken.

What survives:

CAPAS targets a narrower failure mode:

```text
scientific evidence overclaiming after computation
```

Not just unsupported citation. Not just unsafe tool use. Not just source
misattribution. The CAPAS failure is:

```text
the number is real, but the conclusion is too strong for the number's evidence
type.
```

Claim allowed:

```text
CAPAS is claim-safety middleware for scientific computation agents, scoped to
evidence overclaiming.
```

Claim not allowed:

```text
CAPAS is a general agent safety system.
```

Minimum test:

Use a real LLM-agent output corpus, not only scripted traces, and measure how
often CAPAS rejects overclaims humans agree are overclaims.

Current status:

not proven; only scripted-agent seed exists.

### 8. Typed gold instead of gold traces

Intuition:

"Gold" is not one thing; gold provenance, gold numeric output, gold inference,
and gold physical evidence are different.

Hostile SotA:

Golden traces, agent benchmarks, verified traces, and nanopublications exist.
Broad "gold traces" are taken.

What survives:

CAPAS makes gold typed:

- provenance-gold
- model-solve-gold
- physical-match-gold
- inference-gold
- failure-gold
- rejection-gold
- no-evidence-gold

Claim allowed:

```text
CAPAS distinguishes typed gold states and refuses to use provenance-gold as
physical/inference gold.
```

Claim not allowed:

```text
CAPAS invented golden scientific traces.
```

Minimum test:

The audit gate must keep `fine_tune_ready=False` unless inference and physical
evidence are independently accepted.

Current status:

covered: coverage-ready but not fine-tune-ready.

### 9. Corpus as an ontology of scientific error

Intuition:

The corpus is no longer just examples; it is a minimal ontology of scientific
error/ambiguity classes.

Hostile SotA:

VVUQ, uncertainty quantification, error taxonomies, scientific workflow
provenance, and agent failure taxonomies already classify errors. Broad error
ontology is taken.

What survives:

CAPAS has an operational taxonomy tied to executable traces:

- solver error
- model error
- reference-definition error
- route rejection
- backend failure
- no evidence
- local-vs-universal mismatch
- formal-vs-estimated bound
- degeneracy
- robust-vs-threshold-barely pass

Claim allowed:

```text
CAPAS provides a trace-backed seed taxonomy of evidence/overclaim errors in
scientific computation agents.
```

Claim not allowed:

```text
CAPAS is a complete ontology of scientific error.
```

Minimum test:

Each error class needs at least one trace and at least one claim-check rule or
audit criterion.

Current status:

partially covered.

### 10. Agent as the real user

Intuition:

The primary user may be a scientific agent, not a human scientist.

Hostile SotA:

Agent provenance, source-aware verification, guardrails, trace safety, and
Toulmin-style CoT evaluation are active in 2026. Broad "middleware for agents"
is taken.

What survives:

CAPAS can be a specialized middleware layer for scientific agents that run
computations and then narrate results.

The target failure is not:

```text
the agent fabricated a citation
```

but:

```text
the agent computed a legitimate number and overstated what that number proves
```

Claim allowed:

```text
CAPAS can serve scientific agents as a post-computation evidence type checker.
```

Claim not allowed:

```text
CAPAS is a general-purpose agent verifier.
```

Minimum test:

Wrap an agent-generated scientific computation, extract its proposed claim, and
check whether CAPAS accepts or rejects the claim from the trace evidence.

Current status:

not proven. `trace_038` is a scripted-agent seed only.

## What This Changes

The strongest surviving phrase is not:

```text
claim safety middleware for scientific agents
```

That is too broad.

The stronger, safer phrase is:

```text
evidence-type checking for scientific computation claims
```

or:

```text
claim licensing over evidence-typed scientific computation traces
```

## Immediate Next Technical Steps

1. Extend `validate_evidence_claims.py` from seed examples into a small rule
   registry with categories:
   - chemistry/model claims
   - optimization claims
   - formal-bound claims
   - universal-anchor claims
   - witness-independence claims

2. Add a claim compiler:

```text
trace -> strongest safe claim(s)
```

3. Add an overclaim corpus:

```text
trace + proposed agent sentence -> ACCEPT/REJECT + reason
```

4. Add at least one real LLM-agent output. Until then, agent-facing claims remain
   unproven.

## Current Non-Degradable Claim

```text
CAPAS does not invent scientific traces, provenance, claim verification,
argumentation, or evidence grading.

CAPAS applies evidence typing to scientific computation results and has a first
executable checker that rejects selected overclaims when the attached physical
or computational evidence does not license them.
```

