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
                        "nickname": "이동우",
                        "user_type": "농인"
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
        "user_type": current_user.user_type
    }