from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.auth.models import User
from core.schemas import RegisterRequest
from core.auth.security import hash_password

router = APIRouter()

@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    # 중복 아이디 검사
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    # 비밀번호 해시화
    hashed_pw = hash_password(request.password)

    new_user = User(
        username=request.username,
        password=hashed_pw,
        nickname=request.nickname,
        user_type=request.user_type,
        emergency_type=request.emergency_type,
        address=request.address,
        organization_name=request.organization_name
    )

    db.add(new_user)
    db.commit()

    return {"message": "회원가입이 완료되었습니다!"}