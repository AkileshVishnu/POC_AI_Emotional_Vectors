import sys
from pprint import pprint
from app.emotion_vectorizer import analyze_emotions


if __name__ == '__main__':
    text = ' '.join(sys.argv[1:])

    if not text:
        print('Usage: python -m app.cli "your text"')
        sys.exit(1)

    pprint(analyze_emotions(text))
