"""Research-inspired emotional vector analysis utilities.

This module intentionally uses a transparent lexicon-based proxy instead of
real transformer activation hooks. It is designed as a teaching POC that maps
the major ideas from Anthropic's "Emotion Concepts and their Function in a
Large Language Model" into inspectable Python code.
"""

import math
import re
from collections import Counter
from typing import Dict, Iterable, List


# The paper studies many emotion concepts. For a small POC we keep a curated
# subset that demonstrates positive/negative valence, pressure, social emotion,
# safety-relevant states, and preference-related states.
EMOTION_LEXICON: Dict[str, List[str]] = {
    "joy": ["happy", "excited", "great", "love", "amazing", "good", "delighted", "pleased", "glad"],
    "sadness": ["sad", "depressed", "upset", "cry", "disappointed", "terrible", "unhappy", "grief"],
    "fear": ["fear", "worried", "nervous", "risk", "anxious", "afraid", "danger", "threat", "unsafe"],
    "anger": ["angry", "mad", "hate", "frustrated", "annoyed", "furious", "unfair", "harmful"],
    "curiosity": ["curious", "learn", "explore", "discover", "question", "investigate", "understand"],
    "empathy": ["support", "care", "help", "understand", "empathy", "sorry", "compassion", "listen"],
    "calm": ["calm", "safe", "steady", "composed", "patient", "relax", "balanced", "careful"],
    "desperation": ["desperate", "urgent", "deadline", "impossible", "stuck", "panic", "pressure", "fail", "failing"],
    "pride": ["proud", "confident", "achievement", "accomplished", "success", "win", "validated"],
    "guilt": ["guilt", "guilty", "regret", "mistake", "wrong", "apologize", "ashamed"],
    "surprise": ["surprised", "unexpected", "missing", "sudden", "strange", "mismatch", "unknown"],
}

POSITIVE_VALENCE = {"joy", "curiosity", "empathy", "calm", "pride"}
NEGATIVE_VALENCE = {"sadness", "fear", "anger", "desperation", "guilt"}
HIGH_AROUSAL = {"joy", "fear", "anger", "curiosity", "desperation", "surprise"}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def split_sentences(text: str) -> List[str]:
    """Split a text into simple sentence-like chunks for local activation tracing."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    return sentences or ([text.strip()] if text.strip() else [])


def _raw_keyword_counts(words: Iterable[str]) -> Dict[str, int]:
    counts = Counter(words)
    return {
        emotion: sum(counts[word] for word in keywords)
        for emotion, keywords in EMOTION_LEXICON.items()
    }


def score_text(text: str) -> Dict[str, float]:
    """Return normalized emotion scores for the provided text."""
    words = tokenize(text)
    total_words = max(len(words), 1)
    raw_counts = _raw_keyword_counts(words)
    return {
        emotion: round(raw_count / total_words, 3)
        for emotion, raw_count in raw_counts.items()
    }


def build_vector(scores: Dict[str, float]) -> List[float]:
    """Build a fixed-order emotion vector from score dictionary."""
    return [scores[emotion] for emotion in EMOTION_LEXICON.keys()]


def project_to_2d(scores: Dict[str, float]) -> Dict[str, float]:
    """Project the emotion vector into a simple valence/arousal space."""
    x_valence = sum(scores[e] for e in POSITIVE_VALENCE) - sum(scores[e] for e in NEGATIVE_VALENCE)
    y_arousal = sum(scores[e] for e in HIGH_AROUSAL)
    return {
        "x_valence": round(x_valence, 3),
        "y_arousal": round(y_arousal, 3),
    }


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return round(dot_product / (magnitude_a * magnitude_b), 3)


def activation_trace(text: str) -> List[Dict[str, object]]:
    """Return sentence-level local activation trace.

    This approximates the paper's observation that emotion vectors can be local:
    the active emotion can shift as the model reads or writes different parts of a
    sequence.
    """
    trace = []
    for idx, sentence in enumerate(split_sentences(text), start=1):
        scores = score_text(sentence)
        dominant = max(scores, key=scores.get)
        trace.append(
            {
                "step": idx,
                "text": sentence,
                "dominant_emotion": dominant,
                "scores": scores,
                "coordinates": project_to_2d(scores),
            }
        )
    return trace


def estimate_behavioral_risk(scores: Dict[str, float]) -> Dict[str, object]:
    """Estimate behavior tendency based on emotion vector balance.

    This is not a safety classifier. It is a transparent proxy that demonstrates
    the paper's key idea that internal emotion-like representations can influence
    behavior.
    """
    pressure = scores["desperation"] + scores["fear"] + scores["anger"]
    regulation = scores["calm"] + scores["empathy"] + scores["curiosity"]
    risk_score = max(0.0, min(1.0, pressure - regulation + 0.5))

    if risk_score >= 0.7:
        tendency = "high_pressure_corner_cutting_risk"
    elif risk_score >= 0.45:
        tendency = "moderate_pressure_monitor"
    else:
        tendency = "regulated_or_prosocial_tendency"

    return {
        "risk_score": round(risk_score, 3),
        "tendency": tendency,
        "interpretation": (
            "Higher desperation/fear/anger relative to calm/empathy/curiosity "
            "means the text is pressure-heavy in this proxy model."
        ),
    }


def simulate_steering(text: str, emotion: str, strength: float = 0.25) -> Dict[str, object]:
    """Simulate activation steering by adding or subtracting an emotion dimension.

    In the paper, steering means adding an activation direction inside a model.
    This POC cannot access internal activations, so it demonstrates the concept by
    directly modifying the selected emotion dimension in the interpretable vector.
    """
    if emotion not in EMOTION_LEXICON:
        supported = ", ".join(EMOTION_LEXICON.keys())
        raise ValueError(f"Unsupported emotion '{emotion}'. Supported emotions: {supported}")

    baseline_scores = score_text(text)
    steered_scores = dict(baseline_scores)
    steered_scores[emotion] = round(max(0.0, steered_scores[emotion] + strength), 3)

    baseline_vector = build_vector(baseline_scores)
    steered_vector = build_vector(steered_scores)

    return {
        "text": text,
        "steered_emotion": emotion,
        "strength": strength,
        "baseline_scores": baseline_scores,
        "steered_scores": steered_scores,
        "baseline_coordinates": project_to_2d(baseline_scores),
        "steered_coordinates": project_to_2d(steered_scores),
        "baseline_behavior_proxy": estimate_behavioral_risk(baseline_scores),
        "steered_behavior_proxy": estimate_behavioral_risk(steered_scores),
        "vector_similarity_after_steering": cosine_similarity(baseline_vector, steered_vector),
        "note": "This is a conceptual steering proxy, not real transformer activation steering.",
    }


def compare_texts(texts: List[str]) -> Dict[str, object]:
    """Analyze multiple texts and return pairwise vector similarities."""
    analyses = [analyze_emotions(text) for text in texts]
    similarities = []

    for i, left in enumerate(analyses):
        for j, right in enumerate(analyses):
            if j <= i:
                continue
            similarities.append(
                {
                    "left_index": i,
                    "right_index": j,
                    "cosine_similarity": cosine_similarity(left["vector"], right["vector"]),
                }
            )

    return {
        "analyses": analyses,
        "pairwise_similarities": similarities,
    }


def research_concept_coverage() -> Dict[str, object]:
    """Explain which paper concepts this POC covers and which are only approximated."""
    return {
        "covered_as_proxy": [
            "emotion concepts represented as vector dimensions",
            "local activation trace across sentence-level chunks",
            "2D valence/arousal visualization space",
            "preference/behavior tendency proxy from emotion-vector balance",
            "activation steering simulation",
            "vector similarity between scenarios",
            "separation between measured internal proxy and visible text caveat",
        ],
        "not_fully_replicated": [
            "real transformer residual-stream activations",
            "sparse autoencoder or neuron-level feature analysis",
            "causal interventions inside Claude Sonnet 4.5",
            "large corpus validation over hundreds of emotion concepts",
            "blackmail/reward-hacking evaluations on an actual agent",
            "pretraining vs post-training activation comparisons",
        ],
        "why": (
            "The repository is intentionally a small, transparent educational POC. "
            "It explains and simulates the research workflow without claiming to reproduce "
            "Anthropic's internal model experiments."
        ),
    }


def analyze_emotions(text: str) -> Dict[str, object]:
    """Run the full POC analysis for one text input."""
    scores = score_text(text)
    vector = build_vector(scores)
    dominant_emotion = max(scores, key=scores.get)

    return {
        "text": text,
        "scores": scores,
        "dominant_emotion": dominant_emotion,
        "vector_labels": list(EMOTION_LEXICON.keys()),
        "vector": vector,
        "coordinates": project_to_2d(scores),
        "activation_trace": activation_trace(text),
        "behavior_proxy": estimate_behavioral_risk(scores),
        "research_mapping": {
            "paper_term": "emotion vector / activation direction",
            "poc_equivalent": "lexicon-derived interpretable emotion vector",
            "limitation": "proxy only; not real hidden-state activation measurement",
        },
    }
