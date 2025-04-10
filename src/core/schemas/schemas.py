from pydantic import BaseModel
from typing import Union, List

# 로그인
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str

# 수어 관련 요청/응답
class TranslationRequest(BaseModel):
    words: List[str]

class TranslationResponse(BaseModel):
    translated_sentence: str
    audio_base64: str

# WebSocket 메시지
class WebSocketMessage(BaseModel):
    type: str
    data: Union[str, dict]