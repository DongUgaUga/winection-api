from fastapi import FastAPI
from slts.websocket_handler import websocket_router

# FastAPI: 애플리케이션 초기화
app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.2"
)

app.include_router(websocket_router)