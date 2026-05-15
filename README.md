# POC AI Emotional Vectors

A lightweight proof-of-concept inspired by the idea of **AI emotional vectors**: representing emotional signals from text as numerical dimensions that can be analyzed, compared, and visualized.

> Note: This project does **not** claim that AI systems truly feel emotions. It demonstrates how emotional language can be converted into interpretable vector features for experimentation, dashboards, and downstream AI-product prototypes.

## What this POC does

- Accepts a text input such as a user message, transcript, or chatbot response.
- Scores the text across simple emotion dimensions.
- Converts emotion scores into a normalized vector.
- Projects the vector into a 2D emotional space.
- Provides a CLI demo, FastAPI endpoint, and unit tests.

## Emotional dimensions

| Dimension | Meaning |
|---|---|
| joy | Positive / happy signal |
| sadness | Sad or disappointed signal |
| fear | Anxiety / risk / threat signal |
| anger | Frustration / conflict signal |
| curiosity | Learning / exploration signal |
| empathy | Supportive / caring signal |

## Folder structure

```text
POC_AI_Emotional_Vectors/
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── cli.py
│   ├── emotion_vectorizer.py
│   └── schemas.py
├── examples/
│   └── sample_inputs.json
├── tests/
│   └── test_emotion_vectorizer.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python -m app.cli "I am excited to learn this but also nervous about the risk."
```

Run the API:

```bash
uvicorn app.api:app --reload
```

Test the API:

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"I am curious and excited, but worried about the deadline."}'
```

Run tests:

```bash
pytest -q
```

## How the scoring works

This POC intentionally uses a transparent lexicon-based approach instead of a black-box model. Each emotion has a small keyword dictionary. The app counts matching words, normalizes by text length, and returns a fixed-length vector.

This makes the POC easy to explain in a GitHub demo and simple to replace later with transformer embeddings, sentiment models, LLM-based labeling, vector databases, and dashboard visualizations.

## Future enhancements

- Add Streamlit UI for live emotional vector visualization.
- Store analyzed messages in SQLite or Snowflake.
- Add sentence-level emotion trajectory.
- Replace lexicon scoring with Hugging Face emotion model.
- Add cosine similarity between messages.
- Add clustering of emotional patterns.
