from pydantic import BaseModel, Field
from typing import Union, List

# 수어 관련 요청/응답
class TranslationRequest(BaseModel):
    words: List[str] = Field(example="['안녕', '이동우', '반갑다']")

class TranslationResponse(BaseModel):
    translated_sentence: str = Field(example="안녕, 동우야. 반가워!")
    audio_base64: str = Field(..., example="UklGRjQAAABXQVZFZm10IBAAAAABAAEA...")

class CreateRoomResponse(BaseModel):
    room_id: str = Field(example="x8p2z1")

class WebSocketMessage(BaseModel):
    type: str
    data: Union[str, dict]
    
class LocationRequest(BaseModel):
    latitude: float = Field(..., example=36.123456)
    longitude: float = Field(..., example=127.456789)