from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from core.db.database import get_db
from core.auth.models import User
from core.schemas.user_schema import ResetPasswordCheckRequest, ResetPasswordRequest
from core.validators.user_validators import validate_password_reset
from core.auth.security import hash_password

router = APIRouter()

@router.post("/password/find")
def find_password(data: ResetPasswordCheckRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.username == data.username,
        User.phone_number == data.phone_number
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="일치하는 회원 정보가 없습니다.")

    return {"message": "비밀번호 재설정이 가능합니다."}

@router.patch("/password/reset")
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