from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.auth.models import User
from core.schemas.user_schema import RegisterRequest
from core.validators.user_validators import validate_register, validate_nickname
from core.auth.security import hash_password
from starlette.status import HTTP_400_BAD_REQUEST

router = APIRouter()

@router.post("/register")
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        validate_register(request, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    hashed_pw = hash_password(request.password)

    new_user = User(
        username=request.username,
        password=hashed_pw,
        nickname=request.nickname,
        phone_number=request.phone_number,
        user_type=request.user_type,
        emergency_type=request.emergency_type,
        address=request.address,
        organization_name=request.organization_name
    )

    db.add(new_user)
    db.commit()

    return {"message": "회원가입이 완료되었습니다!"}

@router.get("/register/nickname-check")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    try:
        validate_nickname(nickname, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "사용 가능한 닉네임입니다."}