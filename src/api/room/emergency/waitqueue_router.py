from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from core.auth.dependencies import get_current_user
from core.auth.models import User
from collections import deque

router = APIRouter()

@router.websocket("/ws/waitqueue/{emergency_code}")
async def deaf_waitqueue_ws(
    ws: WebSocket,
    emergency_code: str,
    current_user: User = Depends(get_current_user)
):
    await ws.accept()

    app = ws.app
    user_id = current_user.id

    # 상태 저장
    app.state.users[user_id] = current_user
    lat, lng = app.state.emergency_locations.get(user_id, (None, None))

    if emergency_code not in app.state.emergency_queues:
        app.state.emergency_queues[emergency_code] = deque()
    app.state.emergency_queues[emergency_code].append((user_id, ws))

    # 응급기관 연결 시 바로 알림 전송
    agency_ws = app.state.emergency_waiting.get(emergency_code)
    if agency_ws:
        await agency_ws.send_json({
            "type": "requestCall",
            "client_id": "peer",
            "data": {
                "user_id": user_id,
                "nickname": current_user.nickname,
                "phone_number": current_user.phone_number,
                "location": {
                    "latitude": lat,
                    "longitude": lng
                }
            }
        })

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        app.state.emergency_queues[emergency_code] = deque([
            (uid, w) for uid, w in app.state.emergency_queues[emergency_code] if uid != user_id
        ])
        app.state.users.pop(user_id, None)
        app.state.emergency_locations.pop(user_id, None)