import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from slts.run_slts import websocket_router
from slts.sentence import word_to_sentence
from slts.speech import text_to_speech

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# FastAPI: 애플리케이션 초기화
app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.2"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (보안이 필요한 경우 특정 도메인만 입력)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# WebSocket: 웹소켓 통신 
app.include_router(websocket_router)

# 요청 데이터 모델 정의
class TranslationRequest(BaseModel):
    words: list[str]  # 수어 단어 리스트

# FastAPI: 문장 변환 및 음성 생성
@app.post("/translate")
async def translate(request: TranslationRequest):
    try:
        # DeepSeek API로 문장 변환
        sentence = word_to_sentence(request.words)
        
        # Google TTS로 음성 변환 (Base64 인코딩된 MP3 반환)
        audio_base64 = text_to_speech("ko-KR-Wavenet-D", sentence)

        return {
            "translated_sentence": sentence,
            "audio_base64": audio_base64  # 프론트에서 Base64 디코딩하여 재생
        }

    except RuntimeError as e:
        logging.error(f"[sentence_builder] 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="sentence_builder 중 오류 발생")