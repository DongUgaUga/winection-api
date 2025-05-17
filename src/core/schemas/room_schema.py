from pydantic import BaseModel, Field
from typing import Union, List, Literal

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
    latitude: float = Field(..., example=36.123456, description="농인의 현재 위도")
    longitude: float = Field(..., example=127.654321, description="농인의 현재 경도")
    emergency_type: Literal["병원", "경찰서", "소방서"] = Field(..., example="병원", description="연결을 원하는 응급기관 종류")
    
class MessageResponse(BaseModel):
    message: str = Field(..., example="요청이 성공적으로 처리되었습니다.")