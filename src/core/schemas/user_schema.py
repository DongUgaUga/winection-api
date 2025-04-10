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
    user_type: str = Field(..., example="농인")

class LoginRequest(BaseModel):
    username: str = Field(example="woo1234")
    password: str = Field(example="woo1234@")

class LoginResponse(BaseModel):
    token: str = Field(example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ3b28xMjM0IiwiaWF0IjoxNjY2NTY4NzQwfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c")