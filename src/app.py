import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR))
sys.path.append(SRC_DIR)

from fastapi import FastAPI
from core.config.cors_config import add_cors_middleware
from core.config.swagger_config import custom_openapi
from api.auth.router import login_router, register_router, password_router
from api.user.router import me_router
from api.room.room_id.router import room_router
from api.room.video.router import video_router
from api.room.emergency.router import location_router
from api.room.emergency.router import waitqueue_router
from api.room.emergency.router import emergency_router

app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.1"
)

add_cors_middleware(app)

app.state.rooms = {}
app.state.pending_signals = {}

app.state.emergency_queues = {}       # 코드별 대기열
app.state.emergency_waiting = {}      # 코드별 응급기관 WebSocket
app.state.emergency_locations = {}    # 농인 위치
app.state.users = {}                  # 농인 전체 정보

app.openapi = lambda: custom_openapi(app)

# 라우터
app.include_router(register_router.router)
app.include_router(login_router.router)
app.include_router(me_router.router)

app.include_router(password_router.router)

app.include_router(room_router.router)
app.include_router(video_router.router)

app.include_router(waitqueue_router.router)
app.include_router(emergency_router.router)
app.include_router(location_router.router)
