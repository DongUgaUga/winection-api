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
    except ValueError as e:
        await ws.close(code=1008, reason=str(e))
        return

    await ws.accept()
    app = ws.app
    user_id = user.id

    app.state.users[user_id] = user
    lat, lng = app.state.emergency_locations.get(user_id, (None, None))

    if emergency_code not in app.state.emergency_queues:
        app.state.emergency_queues[emergency_code] = deque()
    app.state.emergency_queues[emergency_code].append((user_id, ws))

    agency_ws = app.state.emergency_waiting.get(emergency_code)
    if agency_ws:
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
            msg = await ws.receive_json()
            msg_type = msg.get("type")

            if msg_type == "quitCall":

                app.state.emergency_queues[emergency_code] = deque([
                    (uid, w) for uid, w in app.state.emergency_queues[emergency_code]
                    if uid != user_id
                ])
                app.state.users.pop(user_id, None)
                app.state.emergency_locations.pop(user_id, None)

                await ws.close(code=1000, reason="사용자 요청 종료")
                break

    except WebSocketDisconnect:
        app.state.emergency_queues[emergency_code] = deque([
            (uid, w) for uid, w in app.state.emergency_queues[emergency_code]
            if uid != user_id
        ])
        app.state.users.pop(user_id, None)
        app.state.emergency_locations.pop(user_id, None)