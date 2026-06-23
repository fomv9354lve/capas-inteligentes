"""CAPAS Gate — Hugging Face Space (neutral mirror of the deterministic gate).
Your turn: create a Space (SDK: gradio) and push this folder. It runs the SAME engine, not our server."""
import json
import gradio as gr
import capas_sdk

SAMPLES = {
    "Claim drift (association->causal)": ("statistical_confidence",
        '{"p_value":0.03,"alpha":0.05,"effect_direction_confirmed":false}', "X reduces defects by 35%"),
    "Exact solution (valid)": ("exact_model_solution", '{"abs_error":0.0,"tolerance":1e-3}', "exact match"),
}

def run(claim_type, evidence_json, claim_text):
    try:
        ev = json.loads(evidence_json or "{}")
    except Exception as e:
        return f"bad JSON: {e}"
    out = capas_sdk.gate(claim_type, ev, claim_text or claim_type)
    return f"## {out.get('verdict','?')}\n\n{out.get('why','')}\n\n*CAPAS decides whether the evidence licenses the claim — not whether it is true. Same input → same verdict.*"

with gr.Blocks(title="CAPAS Gate") as demo:
    gr.Markdown("# CAPAS — run a claim\nDeterministic admissibility gate. No LLM in the verdict. Reproducible.")
    ct = gr.Textbox(label="claim_type", value="statistical_confidence")
    ev = gr.Code(label="evidence (JSON)", value=SAMPLES["Claim drift (association->causal)"][1], language="json")
    tx = gr.Textbox(label="claim_text", value="X reduces defects by 35%")
    gr.Button("Run CAPAS gate").click(run, [ct, ev, tx], gr.Markdown())

if __name__ == "__main__":
    demo.launch()
