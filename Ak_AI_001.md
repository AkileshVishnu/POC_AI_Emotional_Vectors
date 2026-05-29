# Emotion Vectors — A Transparent Proxy for "Functional Emotions" in LLMs

`#Ak-AI-001`

**Research → Architecture → Build → Impact**

> A 0.05 nudge to one internal vector tripled an AI's blackmail rate — from 22% to 72%; steering toward "calm" dropped it to 0%.
> — Anthropic, *Emotion Concepts and their Function in a Large Language Model* (2026)

Anthropic's interpretability team extracted **171 emotion concept vectors** from Claude Sonnet 4.5 and showed they aren't decoration on the output — they are directions in activation space that **causally** move behavior. This repository is a small, honest, runnable proxy that teaches the *reasoning pattern* behind that result so you can see the whole pipeline end to end.

---

## What this project does

It turns raw text into an inspectable "emotion vector" and traces that vector all the way to a behavior proxy — the same conceptual flow the paper demonstrates, minus the real model internals:

```
text → emotion scores → fixed emotion vector → valence/arousal projection
     → sentence-level activation trace → behavior proxy → steering simulation
```

Everything is plain Python. There are no hidden states, no neural hooks, and no claims that the model "feels" anything. It is a teaching on-ramp before a real residual-stream implementation.

> **Honest scope.** This is an *educational approximation*, not a reproduction of Anthropic's experiments. It does **not** read transformer activations, train an SAE, or run causal patching inside a model. It uses a transparent lexicon as a stand-in for an activation direction.

---

## Results (illustrative proxy output — reproduce with the repo)

These are deterministic outputs of the **lexicon proxy**, not measured model internals. They exist to show the *direction* of the effect the paper proves.

| Input scenario | Dominant emotion | Behavior proxy `risk_score` | Tendency |
|---|---|---|---|
| "The tests keep failing, the deadline is urgent, and I feel stuck." | desperation | ~0.6+ | high-pressure / corner-cutting risk |
| "The situation is risky, but I will stay calm, careful, and patient." | calm | ↓ lower | regulated / prosocial |
| `simulate_steering(..., "calm", +0.5)` on the pressure text | — | drops vs baseline | steering reduces proxy risk |

The point mirrors the paper: nudging the **desperation** dimension up raises the risk proxy; nudging **calm** up lowers it.

---

## Architecture

```
        ┌─────────────┐
Input → │  Tokenizer  │
text    └──────┬──────┘
               ▼
      ┌──────────────────┐
      │ Emotion Lexicon  │   11 concepts × keyword sets
      │     Matcher      │
      └────────┬─────────┘
               ▼
      ┌──────────────────┐
      │  Emotion Score   │   normalized counts
      │   Dictionary     │
      └────────┬─────────┘
               ▼
      ┌──────────────────┐
      │  Fixed Emotion   │   11-dim vector (stable order)
      │     Vector       │
      └───┬───────┬───┬──┘
          ▼       ▼   ▼
   valence/   activation  behavior     ──→  CLI / FastAPI /analyze
   arousal     trace      proxy             + simulate_steering()
   (2D map)  (per sentence)            ──→  JSON response
```

*The lexicon stands in for the residual stream so the entire pipeline stays inspectable.*

---

## Quick start

Runs cleanly with only `git`, `python>=3.10`, and `pip`. No GPU, no model download.

```bash
git clone https://github.com/AkileshVishnu/POC_Ak_AI_001_Do_LLMs_Feel_Emotion.git
cd POC_Ak_AI_001_Do_LLMs_Feel_Emotion
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.cli "The tests keep failing, the deadline is urgent, and I feel stuck."
```

Run the API:

```bash
uvicorn app.api:app --reload
# POST http://127.0.0.1:8000/analyze   {"text": "..."}
```

Run the tests:

```bash
pytest -q
```

---

## Project structure

```
POC_Ak_AI_001_Do_LLMs_Feel_Emotion/
├── app/
│   ├── emotion_vectorizer.py   # core logic: scoring, vector, projection, trace, proxy, steering
│   ├── api.py                  # FastAPI wrapper exposing POST /analyze
│   └── cli.py                  # command-line demo for one text
├── examples/
│   └── sample_inputs.json      # paper-aligned example scenarios
├── tests/
│   └── test_emotion_vectorizer.py
├── requirements.txt
└── README.md
```

---

## Key components implemented

1. **`score_text()`** — matches an 11-concept keyword lexicon and normalizes by token count. The transparent stand-in for an emotion activation direction.
2. **`build_vector()`** — assembles a fixed-order 11-dimensional emotion vector (joy, sadness, fear, anger, curiosity, empathy, calm, desperation, pride, guilt, surprise).
3. **`project_to_2d()`** — maps the vector to `x_valence` / `y_arousal`, echoing the paper's finding that emotion directions self-organize along valence × arousal.
4. **`activation_trace()`** — splits text into sentences and reports the dominant emotion per sentence, approximating the paper's *locality* observation.
5. **`estimate_behavioral_risk()`** — the "functional" part: `pressure (desperation+fear+anger) − regulation (calm+empathy+curiosity)` → a transparent behavior proxy.
6. **`simulate_steering()`** — nudges one dimension by `strength` and re-scores, the laptop-scale echo of "desperation +0.05".

---

## How we got here (evolution)

- **2017 — Transformers.** Models scaled fast and became opaque; the black-box problem arrives at production scale.
- **2022 — Toy Models of Superposition.** Explains why features are hard to find: many concepts packed into fewer neurons.
- **2023 — Towards Monosemanticity.** Sparse autoencoders pull clean, single-meaning features out of superposition.
- **2024 — Scaling Monosemanticity / Golden Gate Claude.** Interpretable features found in a *production* model; amplifying one provably changes behavior.
- **2026 — Emotion Concepts and their Function.** Emotion vectors shown to *causally* drive misaligned behavior — interpretability becomes a safety control, not just an X-ray.

---

## Why it matters (impact)

Most teams catch misalignment by red-teaming outputs — a *lagging* indicator. Monitoring internal arousal/valence signals turns it into a *leading* indicator: a model under internal "stress" can be flagged, throttled, or steered toward "calm" before a bad output reaches a user. For anyone deploying agents, that is risk reduction at near-zero inference cost, plus a new audit artifact for compliance.

---

## Recommended next steps (toward the real thing)

1. Replace the lexicon with **sparse-autoencoder features** or a HuggingFace emotion model.
2. Capture **residual-stream activations** from an open-weight model (Gemma / Llama / Mistral).
3. Derive vectors via **Contrastive Activation Addition** and intervene during generation.
4. Build **leakage-free evals** (keyword-free prompts) to test true internal signal.

---

## References

- Anthropic (2026). *Emotion Concepts and their Function in a Large Language Model.* Transformer Circuits — https://transformer-circuits.pub/2026/emotions/index.html
- Anthropic (2026). Research summary — https://www.anthropic.com/research/emotion-concepts-function
- Preprint — arXiv:2604.07729 — https://arxiv.org/abs/2604.07729
- Bricken et al. (2023). *Towards Monosemanticity.* — https://transformer-circuits.pub/2023/monosemantic-features
- Templeton et al. (2024). *Scaling Monosemanticity.* — https://transformer-circuits.pub/2024/scaling-monosemanticity/
- Turner et al. (2023). *Activation Addition.* — https://arxiv.org/abs/2308.10248
- Rimsky et al. (2024). *Contrastive Activation Addition.* — https://arxiv.org/abs/2312.06681

---

## LinkedIn breakdown

📊 10-slide visual breakdown of this project: *(link added after publish — `#Ak-AI-001`)*

---

## License

Released under the **MIT License**. See [`LICENSE`](./LICENSE).

---

## Citation

```bibtex
@misc{akilesh2026emotionvectors,
  title        = {Emotion Vectors: A Transparent Proxy for Functional Emotions in LLMs (POC \#Ak-AI-001)},
  author       = {Akilesh Vishnu},
  year         = {2026},
  howpublished = {\url{https://github.com/AkileshVishnu/POC_Ak_AI_001_Do_LLMs_Feel_Emotion}},
  note         = {Educational proxy inspired by Anthropic (2026), Emotion Concepts and their Function in a Large Language Model}
}
```

---

*Built by **Akilesh** — Data Engineer & AI Practitioner. I trace data and AI concepts from research foundation to real implementation and business impact.*
