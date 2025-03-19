from pydantic import BaseModel
from typing import List, Any, Union

# TO_SIGN API
class TranslationRequest(BaseModel):
    words: List[str]

# TO_SPEECH API
class TranslationResponse(BaseModel):
    translated_sentence: str
    audio_base64: str

# WebSocket 메시지 구조
class WebSocketMessage(BaseModel):
    type: str
    data: Union[str, dict]

# 로그인 API (추후 추가)
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str