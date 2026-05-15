from fastapi import FastAPI
from pydantic import BaseModel
from app.emotion_vectorizer import analyze_emotions

app = FastAPI(title='POC AI Emotional Vectors')


class EmotionRequest(BaseModel):
    text: str


@app.get('/')
def healthcheck():
    return {'status': 'running'}


@app.post('/analyze')
def analyze(payload: EmotionRequest):
    return analyze_emotions(payload.text)
