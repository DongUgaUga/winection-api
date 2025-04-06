from fastapi import APIRouter, Depends
from core.auth.models import User
from core.auth.dependencies import get_current_user

router = APIRouter()

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "user_type": current_user.user_type
    }