from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from core.auth.models import User
from collections import deque
from datetime import datetime
from core.log.logging import logger
from datetime import datetime, timezone, timedelta
from core.auth.dependencies import get_user_info_from_token

router = APIRouter()

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
        nickname = user_info["nickname"]
        user_type = user_info["user_type"]
    except ValueError as e:
        print("❌ [emergency] 인증 실패:", e)
        await ws.close(code=1008, reason=str(e))
        return

    await ws.accept()
    app = ws.app
    app.state.emergency_waiting[emergency_code] = ws
    print(f"🚨 [emergency] 응급기관 {nickname} 연결됨")

    # 기존 대기열 순회 후 requestCall 전송
    queue = app.state.emergency_queues.get(emergency_code, deque())
    print(f"📋 [emergency] 현재 대기 중인 농인 수: {len(queue)}")

    for uid, deaf_ws in queue:
        target_user = app.state.users.get(uid)
        lat, lng = app.state.emergency_locations.get(uid, (None, None))

        if target_user:
            print(f"📨 [emergency] 농인 {target_user.nickname} 에게 requestCall 전송")
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

                for i, (uid, client_ws) in enumerate(queue):
                    if uid == target_user_id:
                        target_ws = client_ws
                        del queue[i]
                        break

                if not target_ws:
                    print("⚠️ [emergency] 대기열에 해당 농인이 없습니다.")
                    await ws.send_json({
                        "type": "error",
                        "message": "해당 농인이 대기열에 없습니다."
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

                print(f"✅ [emergency] 매칭 완료: {nickname} ↔ {target_user.nickname}")

    except WebSocketDisconnect:
        print(f"🔴 [emergency] 응급기관 {nickname} 연결 종료")
        app.state.emergency_waiting.pop(emergency_code, None)