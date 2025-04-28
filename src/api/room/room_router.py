import random
import string
from fastapi import APIRouter, Request
from core.schemas.room_schema import CreateRoomResponse

router = APIRouter(
    tags=["Room"]
)

def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@router.post(
    "/rooms",
    summary="방 생성",
    description="랜덤한 6자리 영문+숫자 조합으로 새로운 방 ID를 생성하여 반환합니다.",
    response_model=CreateRoomResponse,
    status_code=201,
    responses={
        201: {
            "description": "방 생성 성공",
            "content": {
                "application/json": {
                    "example": {"room_id": "x8p2z1"}
                }
            }
        }
    }
)
async def create_room(request: Request):
    rooms = request.app.state.rooms
    pending = request.app.state.pending_signals
    # 새로운 방 ID 생성
    while True:
        room_id = generate_room_code()
        if room_id not in rooms:
            rooms[room_id] = []           # 방 생성과 동시에
            pending[room_id] = []         # pending_signals 도 초기화
            break
    return {"room_id": room_id}