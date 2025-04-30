from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from core.log.logging import logger
from src.api.room.to_speech.services.sign_to_text import ksl_to_korean

router = APIRouter()
MAX_ROOM_CAPACITY = 2
camera_refresh_tracker = {}

client_labels = {}  # WebSocket 객체 → 'self' or 'peer'

def remove_client(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    if ws in rooms.get(room_id, []):
        rooms[room_id].remove(ws)
    client_labels.pop(ws, None)

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
async def websocket_endpoint(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    pending = ws.app.state.pending_signals

    # 1) 방 체크
    if room_id not in rooms:
        await ws.close(code=1003, reason="존재하지 않는 방입니다.")
        logger.info(f"[{room_id}] 존재하지 않는 방으로의 접속 시도")
        return

    if len(rooms[room_id]) >= MAX_ROOM_CAPACITY:
        await ws.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과로 접속 거부 (현재 인원: {len(rooms[room_id])})")
        return

    # 2) 연결 수락 및 라벨 부여
    await ws.accept()
    rooms[room_id].append(ws)

    label = "self" if len(rooms[room_id]) == 1 else "peer"
    client_labels[ws] = label

    logger.info(f"👤 [{label}] Room:[{room_id}]에 접속했습니다. (현재 인원: {len(rooms[room_id])})")

    # 4) pending 시그널 전송
    if room_id in pending:
        for target_ws, msg in pending[room_id]:
            if target_ws == ws:
                try:
                    await ws.send_text(msg)
                    logger.info(f"[{room_id}] pending 메시지 재전송됨")
                except Exception as e:
                    logger.error(f"[{room_id}] pending 재전송 실패: {e}")
        del pending[room_id]

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
                for peer in list(rooms.get(room_id, [])):
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
                logger.info(f"📨 Room:[{room_id}] - {client_labels.get(ws, 'unknown')} → WebRTC 메시지: {t}")
                payload = json.dumps({"type": t, "data": d})
                for peer in list(rooms.get(room_id, [])):
                    if peer != ws:
                        try:
                            await peer.send_text(payload)
                        except Exception as e:
                            logger.error(f"[{room_id}] WebRTC 전송 실패: {e}")
                            pending.setdefault(room_id, []).append((peer, payload))
                            remove_client(peer, room_id)

            elif t == "camera_state":
                for peer in rooms.get(room_id, []):
                    try:
                        await peer.send_json({
                            "type": "camera_state",
                            "client_id": "peer" if peer != ws else "self",
                            "data": d
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 카메라 상태 전송 실패: {e}")

            elif t == "mic_state":
                for peer in rooms.get(room_id, []):
                    try:
                        await peer.send_json({
                            "type": "mic_state",
                            "client_id": "peer" if peer != ws else "self",
                            "data": d
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 마이크 상태 전송 실패: {e}")

            else:
                logger.warning(f"[{room_id}] 지원되지 않는 메시지 타입: {t}")

    except WebSocketDisconnect:
        logger.info(f"👋 [{client_labels.get(ws, 'unknown')}] Room:[{room_id}]에서 나갔습니다. (현재 인원: {len(rooms[room_id]) - 1})")
        await notify_peer_leave(ws, room_id)
        remove_client(ws, room_id)

    except Exception as e:
        logger.error(f"[{room_id}] websocket 처리 오류: {e}", exc_info=True)
        remove_client(ws, room_id)
