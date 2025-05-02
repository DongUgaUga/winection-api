from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
from core.log.logging import logger
from src.api.room.to_speech.services.sign_to_text import ksl_to_korean
import jwt
from jwt import PyJWTError
from core.db.database import SessionLocal
from core.auth.models import User
from core.auth.dependencies import SECRET_KEY, ALGORITHM
from datetime import datetime

router = APIRouter()

MAX_ROOM_CAPACITY = 4

camera_refresh_tracker: dict[str, dict] = {}
client_labels: dict[WebSocket, str] = {}

user_nicknames: dict[WebSocket, str] = {}
user_types: dict[WebSocket, str] = {}
room_call_start_time: dict[str, str] = {}

def get_user_info_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise ValueError("유효하지 않은 토큰입니다 (sub 없음)")

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()

        if user is None:
            raise ValueError("해당 유저를 찾을 수 없습니다")

        return {
            "nickname": user.nickname,
            "user_type": user.user_type
        } 
    except PyJWTError:
        raise ValueError("유효하지 않은 토큰입니다 (JWT 에러)")

def remove_client(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    if ws in rooms.get(room_id, []):
        rooms[room_id].remove(ws)
    client_labels.pop(ws, None)
    user_nicknames.pop(ws, None) 

async def notify_peer_leave(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    for peer in list(rooms.get(room_id, [])):
        if peer != ws:
            try:
                await peer.send_json({"type": "leave", "client_id": "peer"})
            except Exception as e:
                logger.error(f"[{room_id}] leave 알림 전송 실패: {e}")
                remove_client(peer, room_id)

@router.websocket("/ws/slts/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str, token: str = Query(...)):
    try:
        user_info = get_user_info_from_token(token)
        nickname = user_info["nickname"]
        user_type = user_info["user_type"]
    except ValueError as e:
        await ws.close(code=1008, reason=str(e))
        logger.warning(f"[{room_id}] WebSocket 인증 실패: {e}")
        return
    
    rooms = ws.app.state.rooms
    pending = ws.app.state.pending_signals

    if room_id not in rooms:
        rooms[room_id] = []
        logger.info(f"[{room_id}] 새 방이 생성되었습니다.")
        
        #await ws.close(code=1003, reason="존재하지 않는 방입니다.")
        #logger.info(f"[{room_id}] 존재하지 않는 방으로의 접속 시도")
        return

    if len(rooms[room_id]) >= MAX_ROOM_CAPACITY:
        await ws.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과로 접속 거부 (현재 인원: {len(rooms[room_id])})")
        return

    await ws.accept()
    rooms[room_id].append(ws)
    label = "self" if len(rooms[room_id]) == 1 else "peer"
    client_labels[ws] = label
    user_nicknames[ws] = nickname
    user_types[ws] = user_type
    logger.info(f"👤 [{label}] Room:[{room_id}]에 접속했습니다. (현재 인원: {len(rooms[room_id])})")

    if room_id in pending:
        for target_ws, msg in pending[room_id]:
            if target_ws == ws:
                try:
                    await ws.send_text(msg)
                    logger.info(f"[{room_id}] pending 메시지 재전송됨")
                except Exception as e:
                    logger.error(f"[{room_id}] pending 재전송 실패: {e}")
        del pending[room_id]

    if room_id in camera_refresh_tracker:
        try:
            await ws.send_json({
                "type": "startCall",
                "client_id": "peer" if peer != ws else "self",
                "nickname": user_nicknames.get(ws, "알 수 없음"),
                "user_type": user_types.get(ws, "일반"),
                "started_at": room_call_start_time[room_id]
            })
            logger.info(f"[{room_id}] startCall 메타 재전송됨")
        except Exception as e:
            logger.error(f"[{room_id}] startCall 재전송 실패: {e}")

    try:
        while True:
            data = await ws.receive_text()
            parsed = json.loads(data)
            t = parsed.get("type")
            d = parsed.get("data")

            if t == "land_mark":
                try:
                    prediction = ksl_to_korean(d["land_mark"])
                except Exception:
                    prediction = "예측 실패"
                for peer in list(rooms[room_id]):
                    try:
                        await peer.send_json({
                            "type": "text",
                            "client_id": "peer" if peer != ws else "self",
                            "result": prediction
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 예측 전송 실패: {e}")
                        remove_client(peer, room_id)

            elif t in ["offer", "answer", "candidate"]:
                logger.info(f"Room:[{room_id}] - {client_labels[ws]} → WebRTC 메시지: {t}")
                payload = json.dumps({"type": t, "data": d})
                for peer in list(rooms[room_id]):
                    if peer != ws:
                        try:
                            await peer.send_text(payload)
                        except Exception as e:
                            logger.error(f"[{room_id}] WebRTC 전송 실패: {e}")
                            pending.setdefault(room_id, []).append((peer, payload))
                            remove_client(peer, room_id)

            elif t in ["camera_state", "mic_state"]:
                for peer in rooms[room_id]:
                    try:
                        await peer.send_json({
                            "type": t,
                            "client_id": "peer" if peer != ws else "self",
                            "data": d
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 상태 전송 실패({t}): {e}")

            elif t == "startCall":
                room_call_start_time[room_id] = datetime.now().isoformat() 

                for peer in rooms[room_id]:
                    try:
                        await peer.send_json({
                            "type": "startCall",
                            "client_id": "peer" if peer != ws else "self",
                            "nickname": user_nicknames.get(ws, "알 수 없음"),
                            "user_type": user_types.get(ws, "일반인"), 
                            "started_at": room_call_start_time[room_id]
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] startCall 전송 실패: {e}")
                        #remove_client(peer, room_id)

            else:
                logger.warning(f"[{room_id}] 지원되지 않는 메시지 타입: {t}")

    except WebSocketDisconnect:
        logger.info(f"👋 [{client_labels.get(ws)}] Room:[{room_id}]에서 나갔습니다.")
        await notify_peer_leave(ws, room_id)
        remove_client(ws, room_id)

    except Exception as e:
        logger.error(f"[{room_id}] websocket 처리 오류: {e}", exc_info=True)
        remove_client(ws, room_id)
