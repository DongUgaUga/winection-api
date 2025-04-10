from pydantic import BaseModel, Field
from typing import Literal, Optional
class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    nickname: str
    phone_number: str = Field(
        pattern=r"^01[016789]-?\d{3,4}-?\d{4}$",
        description="형식: 01012345678 또는 010-1234-5678"
    )
    user_type: Literal["농인", "일반인", "응급기관"]
    emergency_type: Optional[Literal["병원", "경찰서", "소방서"]] = None
    address: Optional[str] = None
    organization_name: Optional[str] = None
    
class ResetPasswordCheckRequest(BaseModel):
    username: str
    phone_number: str

class ResetPasswordRequest(BaseModel):
    username: str
    new_password: str
    confirm_password: str