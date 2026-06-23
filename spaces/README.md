---
title: CAPAS Gate
emoji: 🧮
colorFrom: pink
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
license: apache-2.0
---

Neutral mirror of the CAPAS deterministic claim-admissibility gate. Same engine as the reference
implementation; no language model in the verdict. CAPAS decides whether evidence **licenses** a claim,
not whether it is true. To deploy: create a Hugging Face Space (SDK: Gradio) and push this folder.
