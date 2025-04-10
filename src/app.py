import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR))
sys.path.append(SRC_DIR)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from core.config.cors_config import add_cors_middleware
from core.config.swagger_config import custom_openapi
from api.room.to_speech import to_speech_router, translate_router
from api.room.to_sign import to_sign_router
from api.auth import login_router, register_router
from api.user import me_router
from api.room import room_router

app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.1"
)

add_cors_middleware(app)

app.openapi = lambda: custom_openapi(app)

app.include_router(register_router.router)
app.include_router(login_router.router)
app.include_router(me_router.router)

app.include_router(room_router.router)

app.include_router(to_speech_router.router)
app.include_router(to_sign_router.router)

app.include_router(translate_router.router)

# uvicorn src.app:app --host 0.0.0.0 --port 9090 --reload --reload-dir src --ssl-keyfile ./mkcert/key.pem --ssl-certfile ./mkcert/cert.pem