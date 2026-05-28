import pytest

from app.emotion_vectorizer import analyze_emotions, compare_texts, research_concept_coverage, simulate_steering


def test_emotion_analysis():
    text = "I am excited and curious to learn new AI concepts."
    result = analyze_emotions(text)

    assert "scores" in result
    assert result["dominant_emotion"] in result["scores"]
    assert len(result["vector"]) == len(result["vector_labels"])
    assert "activation_trace" in result
    assert "behavior_proxy" in result


def test_sentence_level_activation_trace():
    text = "The deployment failed and the deadline is urgent. I will stay calm and debug carefully."
    result = analyze_emotions(text)

    assert len(result["activation_trace"]) == 2
    assert result["activation_trace"][0]["dominant_emotion"] in result["scores"]


def test_steering_simulation_increases_selected_dimension():
    text = "The tests keep failing and the deadline is urgent."
    result = simulate_steering(text, "calm", 0.5)

    assert result["steered_scores"]["calm"] > result["baseline_scores"]["calm"]
    assert result["note"].startswith("This is a conceptual")


def test_unsupported_steering_emotion():
    with pytest.raises(ValueError):
        simulate_steering("hello", "unsupported_emotion", 0.1)


def test_compare_texts_returns_similarity_pairs():
    result = compare_texts([
        "I am happy and excited.",
        "I am worried and anxious.",
        "I am calm and careful.",
    ])

    assert len(result["analyses"]) == 3
    assert len(result["pairwise_similarities"]) == 3


def test_research_concept_coverage_has_limits():
    coverage = research_concept_coverage()

    assert "covered_as_proxy" in coverage
    assert "not_fully_replicated" in coverage
    assert any("real transformer" in item for item in coverage["not_fully_replicated"])
