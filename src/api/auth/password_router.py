from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.auth.models import User
from core.schemas.user_schema import (
    ResetPasswordCheckRequest,
    ResetPasswordRequest,
    MessageResponse
)
from core.validators.user_validators import validate_password_reset
from core.auth.security import hash_password

router = APIRouter()

@router.post(
    "/password/find",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "비밀번호 재설정 가능",
            "content": {
                "application/json": {
                    "example": {"message": "비밀번호 재설정이 가능합니다."}
                }
            }
        },
        404: {
            "description": "일치하는 회원 정보 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "일치하는 회원 정보가 없습니다."}
                }
            }
        }
    }
)
def find_password(data: ResetPasswordCheckRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username,
        User.phone_number == data.phone_number
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="일치하는 회원 정보가 없습니다.")

    return {"message": "비밀번호 재설정이 가능합니다."}


@router.patch(
    "/password/reset",
    response_model=MessageResponse,
    responses={
        200: {
            "description": "비밀번호 재설정 성공",
            "content": {
                "application/json": {
                    "example": {"message": "비밀번호가 성공적으로 변경되었습니다."}
                }
            }
        },
        400: {
            "description": "비밀번호 불일치 또는 형식 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "비밀번호는 영문, 숫자, 특수문자를 포함한 8자리 이상이어야 합니다."}
                }
            }
        },
        404: {
            "description": "존재하지 않는 유저",
            "content": {
                "application/json": {
                    "example": {"detail": "존재하지 않는 유저입니다."}
                }
            }
        }
    }
)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 유저입니다.")

    try:
        validate_password_reset(data.new_password, data.confirm_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user.password = hash_password(data.new_password)
    db.commit()

    return {"message": "비밀번호가 성공적으로 변경되었습니다."}