from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from core.auth.dependencies import get_current_user
from core.auth.models import User
from collections import deque
from datetime import datetime
from core.log.logging import logger
from datetime import datetime, timezone, timedelta

router = APIRouter()

@router.websocket("/ws/emergency/{emergency_code}")
async def emergency_ws(
    ws: WebSocket,
    emergency_code: str,
    current_user: User = Depends(get_current_user)
):
    await ws.accept()
    app = ws.app

    app.state.emergency_waiting[emergency_code] = ws
    logger.info(f"🚨 응급기관 [{emergency_code}] 연결됨")

    try:
        while True:
            msg = await ws.receive_json()
            msg_type = msg.get("type")
            msg_data = msg.get("data")

            if msg_type == "acceptCall":
                target_user_id = msg_data.get("user_id")
                queue = app.state.emergency_queues.get(emergency_code, deque())
                target_ws = None

                for i, (uid, client_ws) in enumerate(queue):
                    if uid == target_user_id:
                        target_ws = client_ws
                        del queue[i]
                        break

                if not target_ws:
                    await ws.send_json({
                        "type": "error",
                        "message": "해당 농인이 대기열에 없습니다."
                    })
                    continue

                user = app.state.users.get(target_user_id)
                lat, lng = app.state.emergency_locations.get(target_user_id, (None, None))
                KST = timezone(timedelta(hours=9))
                now = datetime.now(KST).isoformat(timespec="seconds")

                await ws.send_json({
                    "type": "startCall",
                    "client_id": "self",
                    "data": {
                        "nickname": user.nickname,
                        "phone_number": user.phone_number,
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
                        "organization_name": current_user.organization_name,
                        "address": current_user.address,
                        "latitude": current_user.latitude,
                        "longitude": current_user.longitude,
                        "start_time": now
                    }
                })

                logger.info(f"[{emergency_code}] 응급기관과 농인 매칭 완료: {user.nickname}")

            else:
                logger.warning(f"알 수 없는 메시지 타입: {msg_type}")

    except WebSocketDisconnect:
        logger.info(f"응급기관 [{emergency_code}] 연결 종료됨")
        app.state.emergency_waiting.pop(emergency_code, None)
