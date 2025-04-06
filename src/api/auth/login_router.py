from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth.models import User
from core.schemas import LoginRequest, LoginResponse
from core.auth.security import verify_password
from api.auth.services.auth import create_access_token

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

    token = create_access_token(data={"sub": user.username})
    return LoginResponse(token=token)