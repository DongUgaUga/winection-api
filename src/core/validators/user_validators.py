import re
from sqlalchemy.orm import Session
from core.schemas.user_schema import RegisterRequest
from core.auth.models import User

def is_nickname_taken(nickname: str, db: Session) -> bool:
    return db.query(User).filter(User.nickname == nickname).first() is not None

def is_username_taken(username: str, db: Session) -> bool:
    return db.query(User).filter(User.username == username).first() is not None

def validate_register(request: RegisterRequest, db: Session):
    validate_password_pair(request.password, request.confirm_password)

    if request.user_type == "응급기관":
        if not all([request.emergency_type, request.address, request.organization_name]):
            raise ValueError("응급기관은 병원/경찰서/소방서, 주소, 기관명을 모두 입력해야 합니다.")

    if is_username_taken(request.username, db):
        raise ValueError("이미 존재하는 아이디입니다.")

    if is_nickname_taken(request.nickname, db):
        raise ValueError("이미 존재하는 닉네임입니다.")

def validate_nickname(nickname: str, db: Session):
    if is_nickname_taken(nickname, db):
        raise ValueError("이미 사용 중인 닉네임입니다.")

def validate_password_pair(password: str, confirm_password: str):
    if password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")
    validate_password_strength(password)

def validate_password_strength(password: str):
    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+]).{8,}$'
    if not re.match(pattern, password):
        raise ValueError("비밀번호는 영문, 숫자, 특수문자를 포함한 8자리 이상이어야 합니다.")
    
def validate_password_reset(new_password: str, confirm_password: str):
    if new_password != confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")
    validate_password_strength(new_password)