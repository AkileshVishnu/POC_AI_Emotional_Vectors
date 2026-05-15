import re
from collections import Counter

EMOTION_LEXICON = {
    'joy': ['happy', 'excited', 'great', 'love', 'amazing', 'good'],
    'sadness': ['sad', 'depressed', 'upset', 'cry', 'disappointed'],
    'fear': ['fear', 'worried', 'nervous', 'risk', 'anxious'],
    'anger': ['angry', 'mad', 'hate', 'frustrated', 'annoyed'],
    'curiosity': ['curious', 'learn', 'explore', 'discover', 'question'],
    'empathy': ['support', 'care', 'help', 'understand', 'empathy']
}


def tokenize(text: str):
    return re.findall(r'\\b\\w+\\b', text.lower())


def analyze_emotions(text: str):
    words = tokenize(text)
    counts = Counter(words)

    total_words = max(len(words), 1)
    scores = {}

    for emotion, keywords in EMOTION_LEXICON.items():
        score = sum(counts[word] for word in keywords) / total_words
        scores[emotion] = round(score, 3)

    dominant_emotion = max(scores, key=scores.get)

    vector = [scores[e] for e in EMOTION_LEXICON.keys()]

    x_valence = round(scores['joy'] - scores['sadness'] - scores['anger'], 3)
    y_arousal = round(scores['fear'] + scores['curiosity'] + scores['joy'], 3)

    return {
        'text': text,
        'scores': scores,
        'dominant_emotion': dominant_emotion,
        'vector': vector,
        'coordinates': {
            'x_valence': x_valence,
            'y_arousal': y_arousal
        }
    }
