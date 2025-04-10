import re
from sqlalchemy.orm import Session
from core.schemas.user_schema import RegisterRequest
from core.auth.models import User

def is_nickname_taken(nickname: str, db: Session) -> bool:
    return db.query(User).filter(User.nickname == nickname).first() is not None

def is_username_taken(username: str, db: Session) -> bool:
    return db.query(User).filter(User.username == username).first() is not None

def validate_register(request: RegisterRequest, db: Session):
    validate_password(request.password, request.confirm_password)
    validate_user_type_fields(request)  # 추가된 부분
    if is_username_taken(request.username, db):
        raise ValueError("이미 존재하는 아이디입니다.")
    if is_nickname_taken(request.nickname, db):
        raise ValueError("이미 존재하는 닉네임입니다.")

def validate_nickname(nickname: str, db: Session):
    if is_nickname_taken(nickname, db):
        raise ValueError("이미 사용 중인 닉네임입니다.")

def validate_password(password: str, confirm_password: str):
    if password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")
    validate_password_strength(password)

def validate_password_strength(password: str):
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+]).{8,}$'
    if not re.match(pattern, password):
        raise ValueError("비밀번호는 영문, 숫자, 특수문자를 포함한 8자리 이상이어야 합니다.")

def validate_user_type_fields(request: RegisterRequest):
    if request.user_type == "응급기관":
        missing_fields = []
        if not request.emergency_type:
            missing_fields.append("emergency_type")
        if not request.address:
            missing_fields.append("address")
        if not request.organization_name:
            missing_fields.append("organization_name")
        if missing_fields:
            raise ValueError(f"응급기관은 다음 필드가 필요합니다: {', '.join(missing_fields)}")