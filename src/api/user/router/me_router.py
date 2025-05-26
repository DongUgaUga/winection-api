from fastapi import APIRouter, Depends
from core.db.models import User
from core.auth.dependencies import get_current_user
from core.schemas.user_schema import CurrentUserResponse

router = APIRouter(
    tags=["User"]
)

@router.get(
    "/me",
    summary="현재 로그인한 사용자 조회",
    description="요청한 JWT 토큰을 기준으로 현재 로그인한 사용자 정보를 반환합니다.",
    response_model=CurrentUserResponse,
    responses={
        200: {
            "description": "현재 로그인한 유저 정보",
            "content": {
                "application/json": {
                    "examples": {
                        "일반 사용자": {
                            "summary": "일반 사용자",
                            "value": {
                                "id": 1,
                                "username": "woo1234",
                                "nickname": "이동우",
                                "phone_number": "010-1111-2222",
                                "user_type": "청인"
                            }
                        },
                        "응급기관 사용자": {
                            "summary": "응급기관 사용자",
                            "value": {
                                "id": 2,
                                "username": "woo123",
                                "nickname": "아파요",
                                "phone_number": "010-1234-5678",
                                "user_type": "응급기관",
                                "emergency_type": "병원",
                                "address": "충남 천안시 동남구 병천면 충절로 1600",
                                "organization_name": "한기대병원",
                                "latitude": "36.7654321",
                                "longitude": "127.1234567",
                                "emergency_code": "a1b2c3d"
                            }
                        }
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
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "phone_number": current_user.phone_number,
        "user_type": current_user.user_type,
    }

    if current_user.user_type == "응급기관":
        user_data.update({
            "emergency_type": current_user.emergency_type,
            "address": current_user.address,
            "organization_name": current_user.organization_name,
            "latitude": current_user.latitude,
            "longitude": current_user.longitude,
            "emergency_code": current_user.emergency_code
        })

    return user_data