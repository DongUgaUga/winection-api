import re
from core.schemas.user_schema import RegisterRequest

def validate_register(request: RegisterRequest):
    if request.password != request.confirm_password:
        raise ValueError("비밀번호가 일치하지 않습니다.")

    pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()_+]).{8,}$'
    if not re.match(pattern, request.password):
        raise ValueError("비밀번호는 영문, 숫자, 특수문자를 포함한 8자리 이상이어야 합니다.")

    if request.user_type == "응급기관":
        if not all([request.emergency_type, request.address, request.organization_name]):
            raise ValueError("응급기관은 병원/경찰서/소방서, 주소, 기관명을 모두 입력해야 합니다.")