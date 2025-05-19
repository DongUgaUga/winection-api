from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.auth.dependencies import get_user_info_from_token
from collections import deque

router = APIRouter()

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.auth.dependencies import get_user_info_from_token
from collections import deque

router = APIRouter()

@router.websocket("/ws/waitqueue/{emergency_code}")
async def deaf_waitqueue_ws(
    ws: WebSocket,
    emergency_code: str,
    token: str = Query(...)
):
    try:
        user_info = get_user_info_from_token(token)
        user = user_info["user"]
        nickname = user_info["nickname"]
        user_type = user_info["user_type"]
    except ValueError as e:
        print("❌ [waitqueue] 인증 실패:", e)
        await ws.close(code=1008, reason=str(e))
        return

    await ws.accept()
    app = ws.app
    user_id = user.id

    # 상태 저장
    app.state.users[user_id] = user
    lat, lng = app.state.emergency_locations.get(user_id, (None, None))

    if emergency_code not in app.state.emergency_queues:
        app.state.emergency_queues[emergency_code] = deque()
    app.state.emergency_queues[emergency_code].append((user_id, ws))
    print(f"🟢 [waitqueue] 농인 {nickname} ({user_id}) 대기열에 등록됨")

    # 응급기관에게 requestCall 전송
    agency_ws = app.state.emergency_waiting.get(emergency_code)
    if agency_ws:
        print(f"📨 [waitqueue] 응급기관 연결됨 → requestCall 전송 시도")
        await agency_ws.send_json({
            "type": "requestCall",
            "client_id": "peer",
            "data": {
                "user_id": user_id,
                "nickname": user.nickname,
                "phone_number": user.phone_number,
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
        print(f"🔴 [waitqueue] 농인 {nickname} 연결 종료")
        app.state.emergency_queues[emergency_code] = deque([
            (uid, w) for uid, w in app.state.emergency_queues[emergency_code] if uid != user_id
        ])
        app.state.users.pop(user_id, None)
        app.state.emergency_locations.pop(user_id, None)