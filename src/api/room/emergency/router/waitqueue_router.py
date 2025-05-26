from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.auth.dependencies import get_user_info_from_token, get_db_context
from collections import deque
from sqlalchemy.exc import SQLAlchemyError
from starlette.websockets import WebSocketState
from core.log.logging import logger

router = APIRouter()

@router.websocket("/ws/waitqueue/{emergency_code}")
async def deaf_waitqueue_ws(
    ws: WebSocket,
    emergency_code: str,
    token: str = Query(...)
):
    try:
        with get_db_context() as db:
            user = get_user_info_from_token(token, db)
    except ValueError as e:
        await ws.close(code=1008, reason=str(e))
        return
    except SQLAlchemyError:
        await ws.close(code=1011, reason="DB 연결 실패")
        return

    await ws.accept()

    app = ws.app
    user_id = user.id

    if not hasattr(app.state, "emergency_waiting"):
        app.state.emergency_waiting = {}
    if not hasattr(app.state, "emergency_queues"):
        app.state.emergency_queues = {}
    if not hasattr(app.state, "users"):
        app.state.users = {}
    if not hasattr(app.state, "emergency_locations"):
        app.state.emergency_locations = {}

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

    async def notify_cancellation():
        agency_ws = app.state.emergency_waiting.get(emergency_code)
        if agency_ws and agency_ws.application_state == WebSocketState.CONNECTED:
            try:
                await agency_ws.send_json({
                    "type": "cancelCall",
                    "data": {
                        "user_id": user_id
                    }
                })
            except Exception as e:
                logger.error(f"agency_ws 전송 실패: {e}")

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
                await notify_cancellation()
                await ws.close(code=1000, reason="사용자 요청 종료")
                break

    except WebSocketDisconnect:
        queue = app.state.emergency_queues.get(emergency_code)
        if queue:
            app.state.emergency_queues[emergency_code] = deque([
                (uid, w) for uid, w in queue if uid != user_id
            ])

        app.state.users.pop(user_id, None)
        app.state.emergency_locations.pop(user_id, None)

        await notify_cancellation()
