from pydantic import BaseModel
from typing import List, Any, Union

from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    name = mapped_column(String(255), nullable=False)
    email = mapped_column(String(255), unique=True, nullable=False)
    posts = relationship("Post",back_populates="owner", cascade='delete')
    is_active = mapped_column(Boolean,default=False)

class Post(Base):
    __tablename__ = "posts"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    title = mapped_column(String(255), nullable=False)
    description = mapped_column(String(255))
    owner_id = mapped_column(Integer, ForeignKey("users.id"))
    owner = relationship("User",back_populates="posts")


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