from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError
from core.schemas.room_schema import WebSocketMessage
from core.log.logging import logger
from src.api.room.to_speech.services.sign_to_text import ksl_to_korean

router = APIRouter()
rooms: dict[str, list[WebSocket]] = {}
pending_signals: dict[str, list[tuple[WebSocket, dict]]] = {}
MAX_ROOM_CAPACITY = 2

def remove_client(ws: WebSocket, room_id: str):
    if ws in rooms.get(room_id, []):
        rooms[room_id].remove(ws)
        if not rooms[room_id]:
            del rooms[room_id]

async def notify_peer_leave(ws: WebSocket, room_id: str):
    for peer in rooms.get(room_id, []):
        if peer is not ws:
            try:
                await peer.send_json({"type": "leave", "client_id": "peer"})
            except Exception as e:
                logger.error(f"[{room_id}] leave 전송 실패: {e}")
                remove_client(peer, room_id)

async def broadcast_signal(sender: WebSocket, room_id: str, msg_type: str, data: dict):
    for peer in list(rooms.get(room_id, [])):
        if peer is not sender:
            try:
                await peer.send_json({"type": msg_type, "data": data})
            except Exception:
                # 실패한 피어는 pending에 저장 후 제거
                pending_signals.setdefault(room_id, []).append((peer, {"type": msg_type, "data": data}))
                remove_client(peer, room_id)

async def broadcast_media_state(sender: WebSocket, room_id: str, state_type: str, data: dict):
    for peer in list(rooms.get(room_id, [])):
        try:
            await peer.send_json({
                "type": state_type,
                "client_id": "peer" if peer is not sender else "self",
                "data": data
            })
        except Exception as e:
            logger.error(f"[{room_id}] {state_type} 전송 실패: {e}")
            remove_client(peer, room_id)

async def broadcast_start_call(room_id: str, nickname: str, start_time: str):
    for peer in rooms.get(room_id, []):
        try:
            await peer.send_json({
                "type": "startCall",
                "data": {"nickname": nickname, "startTime": start_time}
            })
        except Exception as e:
            logger.error(f"[{room_id}] startCall 전송 실패: {e}")

async def broadcast_landmark(sender: WebSocket, room_id: str, landmark):
    try:
        result = ksl_to_korean(landmark)
    except Exception as e:
        logger.error(f"[{room_id}] 예측 오류: {e}")
        result = "예측 실패"

    for peer in list(rooms.get(room_id, [])):
        try:
            await peer.send_json({
                "type": "text",
                "client_id": "peer" if peer is not sender else "self",
                "result": result
            })
        except Exception as e:
            logger.error(f"[{room_id}] 텍스트 전송 실패: {e}")
            remove_client(peer, room_id)

@router.websocket("/ws/slts/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str):
    if room_id not in rooms:
        rooms[room_id] = []
    if len(rooms[room_id]) >= MAX_ROOM_CAPACITY:
        await ws.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과로 접속 거부됨")
        return

    await ws.accept()
    rooms[room_id].append(ws)
    logger.info(f"[{room_id}] 클라이언트 접속 (총 {len(rooms[room_id])}명)")

    if room_id in pending_signals:
        for peer, msg in pending_signals.pop(room_id):
            try:
                await peer.send_json(msg)
                logger.info(f"[{room_id}] pending 메시지 재전송")
            except Exception as e:
                logger.error(f"[{room_id}] pending 재전송 실패: {e}")

    try:
        while True:
            raw = await ws.receive_text()

            try:
                msg = WebSocketMessage.parse_raw(raw)
            except ValidationError as e:
                logger.error(f"[{room_id}] 메시지 검증 실패: {e}")
                continue

            t, d = msg.type, msg.data
            if t in ("offer", "answer", "candidate"):
                await broadcast_signal(ws, room_id, t, d)
            elif t == "startCall":
                nick = d.get("nickname"); st = d.get("startTime")
                logger.info(f"[{room_id}] startCall: {nick} @ {st}")
                await broadcast_start_call(room_id, nick, st)
            elif t in ("camera_state", "mic_state"):
                await broadcast_media_state(ws, room_id, t, d)
            elif t == "land_mark":
                await broadcast_landmark(ws, room_id, d.get("land_mark"))
            else:
                logger.warning(f"[{room_id}] 알 수 없는 메시지 타입: {t}")
                continue

    except WebSocketDisconnect:
        logger.info(f"[{room_id}] 클라이언트 연결 종료")
    except Exception as e:
        logger.error(f"[{room_id}] WebSocket 처리 오류: {e}")
    finally:
        await notify_peer_leave(ws, room_id)
        remove_client(ws, room_id)
        logger.info(f"[{room_id}] 클라이언트 제거 (남은 {len(rooms.get(room_id, []))}명)")
