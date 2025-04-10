from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db.database import get_db
from core.auth.models import User
from core.schemas.user_schema import RegisterRequest, MessageResponse
from core.validators.user_validators import validate_register, validate_nickname
from core.auth.security import hash_password

router = APIRouter()

@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=201,
    responses={
        201: {
            "description": "회원가입 성공",
            "content": {
                "application/json": {
                    "example": {"message": "회원가입이 완료되었습니다!"}
                }
            }
        },
        400: {
            "description": "입력값 오류 또는 중복",
            "content": {
                "application/json": {
                    "example": {"detail": "다음 필드가 누락되었습니다: phone_number"}
                }
            }
        }
    }
)
def register_user(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        validate_register(request, db)  # 검증 로직을 여기에서 호출
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


@router.get(
    "/register/nickname",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "사용 가능한 닉네임",
            "content": {
                "application/json": {
                    "example": {"message": "사용 가능한 닉네임입니다."}
                }
            }
        },
        400: {
            "description": "중복된 닉네임",
            "content": {
                "application/json": {
                    "example": {"detail": "이미 사용 중인 닉네임입니다."}
                }
            }
        }
    }
)
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    try:
        validate_nickname(nickname, db)  # 닉네임 중복 확인
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "사용 가능한 닉네임입니다."}