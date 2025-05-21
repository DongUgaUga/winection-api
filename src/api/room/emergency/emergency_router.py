from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.auth.dependencies import get_user_info_from_token
from collections import deque
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.websocket("/ws/emergency/{emergency_code}")
async def emergency_ws(
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
    if not hasattr(app.state, "emergency_waiting"):
        app.state.emergency_waiting = {}
    if not hasattr(app.state, "emergency_queues"):
        app.state.emergency_queues = {}
    if not hasattr(app.state, "users"):
        app.state.users = {}
    if not hasattr(app.state, "emergency_locations"):
        app.state.emergency_locations = {}

    app.state.emergency_waiting[emergency_code] = ws

    queue = app.state.emergency_queues.get(emergency_code, deque())
    for uid, deaf_ws in queue:
        target_user = app.state.users.get(uid)
        lat, lng = app.state.emergency_locations.get(uid, (None, None))

        if target_user:
            await ws.send_json({
                "type": "requestCall",
                "client_id": "peer",
                "data": {
                    "user_id": uid,
                    "nickname": target_user.nickname,
                    "phone_number": target_user.phone_number,
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
            msg_data = msg.get("data")

            if msg_type == "acceptCall":
                target_user_id = msg_data.get("user_id")
                queue = app.state.emergency_queues.get(emergency_code, deque())
                target_ws = None

                # 최신 큐 상태를 반영하여, 농인이 이미 빠진 경우를 처리
                for i, (uid, client_ws) in enumerate(queue):
                    if uid == target_user_id:
                        target_ws = client_ws
                        del queue[i]
                        break

                # 만약 대기열에서 사라졌다면 cancelCall 전송
                if not target_ws or target_user_id not in app.state.users:
                    await ws.send_json({
                        "type": "cancelCall",
                        "data": {
                            "user_id": target_user_id
                        }
                    })
                    continue

                target_user = app.state.users.get(target_user_id)
                lat, lng = app.state.emergency_locations.get(target_user_id, (None, None))
                now = datetime.now(timezone(timedelta(hours=9))).isoformat(timespec="seconds")

                await ws.send_json({
                    "type": "startCall",
                    "client_id": "self",
                    "data": {
                        "nickname": target_user.nickname,
                        "phone_number": target_user.phone_number,
                        "location": {
                            "latitude": lat,
                            "longitude": lng
                        },
                        "start_time": now
                    }
                })

                await target_ws.send_json({
                    "type": "startCall",
                    "client_id": "peer",
                    "data": {
                        "organization_name": user.organization_name,
                        "address": user.address,
                        "latitude": user.latitude,
                        "longitude": user.longitude,
                        "start_time": now
                    }
                })

            elif msg_type == "readyCall":
                app.state.emergency_waiting[emergency_code] = ws

                queue = app.state.emergency_queues.get(emergency_code, deque())
                for uid, deaf_ws in queue:
                    target_user = app.state.users.get(uid)
                    lat, lng = app.state.emergency_locations.get(uid, (None, None))

                    if target_user:
                        await ws.send_json({
                            "type": "requestCall",
                            "client_id": "peer",
                            "data": {
                                "user_id": uid,
                                "nickname": target_user.nickname,
                                "phone_number": target_user.phone_number,
                                "location": {
                                    "latitude": lat,
                                    "longitude": lng
                                }
                            }
                        })

    except WebSocketDisconnect:
        app.state.emergency_waiting.pop(emergency_code, None)
        app.state.emergency_queues.pop(emergency_code, None)