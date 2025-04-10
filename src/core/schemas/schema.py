from pydantic import BaseModel, Field
from typing import Union, List

# 수어 관련 요청/응답
class TranslationRequest(BaseModel):
    words: List[str] = Field(example="['안녕', '이동우', '반갑다']")

class TranslationResponse(BaseModel):
    translated_sentence: str = Field(example="안녕, 동우야. 반가워!")
    audio_base64: str

# WebSocket 메시지
class WebSocketMessage(BaseModel):
    type: str
    data: Union[str, dict]