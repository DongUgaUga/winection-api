import os
from dotenv import load_dotenv

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt import PyJWTError

from sqlalchemy.orm import Session
from core.auth.models import User
from core.db.database import get_db
from core.db.database import SessionLocal

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="토큰이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유저를 찾을 수 없습니다."
        )
    return user

def get_user_info_from_token(token: str) -> dict:
    try:
        print("🟡 [DEBUG] 받은 token:", token)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("🟢 [DEBUG] 디코딩된 payload:", payload)

        username = payload.get("sub")
        print("🔵 [DEBUG] 추출된 username(sub):", username)

        if not username:
            raise ValueError("토큰에 sub가 없습니다")

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()

        print("🟣 [DEBUG] 조회된 유저:", user)

        if not user:
            raise ValueError("유저가 존재하지 않습니다")

        return {
            "user": user,
            "nickname": user.nickname,
            "user_type": user.user_type
        }
    except PyJWTError as e:
        print("❌ [ERROR] JWT 디코딩 실패:", e)
        raise ValueError("JWT 디코딩 실패")
