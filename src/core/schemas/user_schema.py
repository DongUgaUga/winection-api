from pydantic import BaseModel, Field
from typing import Literal, Optional

class RegisterRequest(BaseModel):
    username: str = Field(example="woo1234")
    password: str = Field(example="woo1234@")
    confirm_password: str = Field(example="woo1234@")
    nickname: str = Field(example="이동우")
    phone_number: str = Field(
        pattern=r"^01[016789]-?\d{4}-?\d{4}$",
        description="형식: 01012345678 또는 010-1234-5678",
        example="010-1234-5678"
    )
    user_type: Literal["농인", "일반인", "응급기관"] = Field(example="농인")
    emergency_type: Optional[Literal["병원", "경찰서", "소방서"]] = Field(None, example="병원")
    address: Optional[str] = Field(None, example="충청남도 천안시 동남구 충절로 1600")
    latitude: Optional[float] = Field(None, example=36.7654321)
    longitude: Optional[float] = Field(None, example=127.1234567)
    organization_name: Optional[str] = Field(None, example="한기대병원")
    

class MessageResponse(BaseModel):
    message: str = Field(..., example="요청이 성공적으로 처리되었습니다.")

class ResetPasswordCheckRequest(BaseModel):
    username: str = Field(example="woo1234")
    phone_number: str = Field(example="010-1234-5678")

class ResetPasswordRequest(BaseModel):
    username: str = Field(example="woo1234@")
    new_password: str = Field(example="woo!5678")
    confirm_password: str = Field(example="woo!5678")
    
class CurrentUserResponse(BaseModel):
    id: int = Field(..., example=1)
    username: str = Field(..., example="woo1234")
    nickname: str = Field(..., example="이동우")
    phone_number: str = Field(..., example="010-1111-2222")
    user_type: str = Field(..., example="응급기관")
    emergency_type: Optional[str] = Field(None, example="병원")
    address: Optional[str] = Field(None, example="충남 천안시 동남구 병천면 충절로 1600")
    organization_name: Optional[str] = Field(None, example="한기대병원")
    latitude: Optional[float] = Field(None, example=36.7654321)
    longitude: Optional[float] = Field(None, example=127.1234567)
    emergency_code: Optional[str] = Field(None, example="abc1234")

class LoginRequest(BaseModel):
    username: str = Field(example="woo1234")
    password: str = Field(example="woo1234@")

class LoginResponse(BaseModel):
    token: str = Field(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0bWR3bjQzMjEiLCJleHAiOjE3NDQ0NjEyMjR9.n85SNI5ul_cKxluT4G3hl9td4Bu2L1Vk_tr2SXHI_f8")