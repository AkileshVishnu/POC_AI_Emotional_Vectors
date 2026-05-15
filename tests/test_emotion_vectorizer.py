from app.emotion_vectorizer import analyze_emotions


def test_emotion_analysis():
    text = 'I am excited and curious to learn new AI concepts.'
    result = analyze_emotions(text)

    assert 'scores' in result
    assert result['dominant_emotion'] in result['scores']
    assert len(result['vector']) == 6
