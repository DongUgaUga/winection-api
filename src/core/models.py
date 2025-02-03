from pydantic import BaseModel
from typing import List, Any

# STSL API
class TranslationRequest(BaseModel):
    words: List[str]

# SLTS API
class TranslationResponse(BaseModel):
    translated_sentence: str
    audio_base64: str

# WebSocket 메시지 구조
class WebSocketMessage(BaseModel):
    type: str
    data: dict[str, Any]

# 로그인 API (추후 추가)
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str