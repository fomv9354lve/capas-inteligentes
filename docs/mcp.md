# CAPAS as an MCP server — the deterministic gate for any LLM agent

CAPAS exposes its fail-closed claim-admissibility gate as **MCP tools**, so any MCP client
(Claude Code, Claude Desktop, Cursor, …) can call it. The agent **proposes** evidence; CAPAS
**disposes** the verdict — and **no language model is ever in the decision**.

## Install (Claude Code / Claude Desktop / Cursor)

Add to your MCP config (e.g. `~/.claude.json` or the client's `mcpServers` block):

```json
{
  "mcpServers": {
    "capas": { "command": "python3", "args": ["/ABS/PATH/TO/capas_mcp.py"] }
  }
}
```

No dependencies — `capas_mcp.py` speaks MCP over stdio (newline-delimited JSON-RPC 2.0) using
only the Python standard library. Verify it locally:

```bash
python3 benchmarks/verify_mcp_server.py     # drives the server as a client; all tools deterministic
```

## Tools

| tool | what it does | catches |
|---|---|---|
| `capas_gate` | gate a structured claim → ACCEPT / REWRITE / REJECT / HOLD | unsupported claims passed off as accepted (HOLDs, never false-ACCEPTs) |
| `capas_invariants` | check declared quantities vs domain LAWS (cross-domain) | finance / psychology / quantum fabrication, one mechanism |
| `capas_gate_quantum` | gate a quantum calibration/result row vs textbook physics | T2>2T1, P01<P10, CZ≫RZZ, too-clean gate error, high ZZ |
| `capas_reward` | dense verifiable reward in [0,1] aligned with the gate | a model gaming the signal by being plausible (RLVR) |
| `capas_certificate` | re-derivable admissibility certificate (audit artifact) | claims with no grounded / generated / unknowable stratification |

## The pattern

```
LLM agent  --proposes evidence-->  CAPAS (capas_mcp)  --gates fail-closed-->  verdict
                                                        (deterministic, no LLM)
```

An agent that returns `verdict: ACCEPT` in its own text is ignored — only the deterministic gate
on the proposed evidence decides. Extraction/grounding reaches record↔text, never text↔reality:
a source that lies about its methods still passes (the GIGO ceiling). CAPAS raises the cost of an
unsupported claim from "assert it" to "make it survive a deterministic gate."
