from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.auth.models import User
from core.schemas.user_schema import LoginRequest, LoginResponse
from core.auth.security import verify_password
from api.auth.services.auth import create_access_token

router = APIRouter(
    tags=["Auth"]
)

@router.post(
    "/login",
    summary="로그인",
    description="사용자의 아이디와 비밀번호를 검증하고, 유효하면 JWT 토큰을 발급합니다.",
    response_model=LoginResponse,
    responses={
        200: {
            "description": "JWT 토큰 반환 성공",
            "content": {
                "application/json": {
                    "example": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                    }
                }
            }
        },
        401: {
            "description": "인증 실패 (아이디 또는 비밀번호 오류)",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "아이디 또는 비밀번호가 올바르지 않습니다."
                    }
                }
            }
        }
    }
)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    
    token = create_access_token(data={"sub": user.username})
    return LoginResponse(token=token)