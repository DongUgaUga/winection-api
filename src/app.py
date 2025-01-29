import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import logging
from fastapi import FastAPI, HTTPException
from slts.websocket_handler import websocket_router
from pydantic import BaseModel
from slts.sentence_builder import generate_sentence_from_words

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# FastAPI: 애플리케이션 초기화
app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.2"
)

# 웹소켓 통신 
app.include_router(websocket_router)

# 요청 데이터 모델 정의
class TranslationRequest(BaseModel):
    words: list[str]  # 수어 단어 리스트

# 문장 변환 엔드포인트
@app.post("/translate")
async def translate(request: TranslationRequest):
    try:
        sentence = generate_sentence_from_words(request.words)
        return sentence
    except RuntimeError as e:
        logging.error(f"[Translate] DeepSeek API 호출 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="DeepSeek API 호출 실패")