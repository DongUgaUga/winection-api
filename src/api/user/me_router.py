from fastapi import APIRouter, Depends
from core.auth.models import User
from core.auth.dependencies import get_current_user
from core.schemas.user_schema import CurrentUserResponse

router = APIRouter()

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    responses={
        200: {
            "description": "현재 로그인한 유저 정보",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "username": "woo1234",
                        "nickname": "응급기관",
                        "phone_number": "010-1234-5678",
                        "user_type": "응급기관",
                        "emergency_type": "병원",
                        "address": "충남 천안시 동남구 병천면 충절로 1600",
                        "organization_name": "한기대병원"
                    }
                }
            }
        },
        401: {
            "description": "토큰 없음 또는 인증 실패",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "토큰이 유효하지 않습니다."
                    }
                }
            }
        }
    }
)
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "phone_number": current_user.phone_number,
        "user_type": current_user.user_type,
        "emergency_type": current_user.emergency_type,
        "address": current_user.address,
        "organization_name": current_user.organization_name,
    }