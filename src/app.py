import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR))
sys.path.append(SRC_DIR)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from core.models import TranslationRequest, TranslationResponse
from core.logging import logger
from api.to_speech.to_speech_router import to_speech_router
from api.to_sign.to_sign_router import to_sign_router
from src.api.to_speech.services.sentence import word_to_sentence
from src.api.to_speech.services.speech import text_to_speech

# FastAPI: 애플리케이션 초기화
app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.2"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://winection.kro.kr, https://api.winection.kro.kr"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket: 웹소켓 통신 
app.include_router(to_speech_router)
app.include_router(to_sign_router)

# get 요청 테스트용
@app.get("/")
async def root():
    return {"message": "API is running"}

# FastAPI: 문장 변환 및 음성 생성
@app.post("/translate", response_model=TranslationResponse)
async def translate(request: TranslationRequest):
    try:
        logger.info("🔍 번역 요청 수신: %s", request.words)
        # DeepSeek API로 문장 변환
        sentence = word_to_sentence(request.words)

        # Google TTS로 음성 변환 (Base64 인코딩된 MP3 반환)
        audio_base64 = text_to_speech("ko-KR-Wavenet-D", sentence)

        return TranslationResponse(translated_sentence=sentence, audio_base64=audio_base64)

    except RuntimeError as e:
        logger.error(f"[sentence_builder] 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="sentence_builder 중 오류 발생")
