from pydantic import BaseModel, model_validator
from typing import Literal, Optional, Union, List


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    nickname: str
    user_type: Literal["농인", "일반인", "응급기관"]

    emergency_type: Optional[Literal["병원", "경찰서", "소방서"]] = None
    address: Optional[str] = None
    organization_name: Optional[str] = None

    @model_validator(mode="after")
    def validate_fields(self):
        if self.password != self.confirm_password:
            raise ValueError("비밀번호가 일치하지 않습니다.")

        if self.user_type == "응급기관":
            if not all([self.emergency_type, self.address, self.organization_name]):
                raise ValueError("응급기관은 병원/경찰서/소방서, 주소, 기관명을 모두 입력해야 합니다.")
        return self

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