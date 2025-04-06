import random
import string
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .to_speech import rooms  # 이미 WebSocket에서 공유 중인 rooms 딕셔너리 사용

room_router = APIRouter()

def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

@room_router.post("/rooms")
async def create_room():
    while True:
        room_id = generate_room_code()
        if room_id not in rooms:
            rooms[room_id] = []
            break
    return JSONResponse(content={"room_id": room_id})