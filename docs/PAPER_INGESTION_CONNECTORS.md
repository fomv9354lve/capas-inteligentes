# CAPAS Paper Ingestion Connectors

CAPAS supports three ingestion levels.

## Level 1: browser preview

Paste paper text or local metadata JSON into the browser. CAPAS extracts
candidate structured claims from explicit spans, requires human confirmation,
and then runs the deterministic gate.

## Level 2: local CLI pipeline

```bash
capas retrieve --input examples/standalone_pipeline_semantic_hold.json --json
capas extract --input examples/standalone_pipeline_semantic_hold.json --json
capas pipeline --input examples/standalone_pipeline_semantic_hold.json --json
```

PDF parsing is available through the standalone pipeline path when local parser
dependencies are installed; failures are declared instead of silently inferred.

## Level 3: source adapters

Current browser adapter accepts Semantic Scholar/PubMed-like metadata exports
with fields such as DOI, title, abstract, and external IDs. Hosted integrations
should resolve DOIs upstream, then pass explicit text spans into CAPAS.
