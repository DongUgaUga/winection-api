from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.schemas.room_schema import WebSocketMessage
import json
from core.log.logging import logger
from src.api.room.to_speech.services.text import ksl_to_korean  # ← 예측 함수 import

router = APIRouter()
rooms = {}
MAX_ROOM_CAPACITY = 2

def remove_client(websocket: WebSocket, room_id: str):
    if websocket in rooms.get(room_id, []):
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:
            del rooms[room_id]

async def notify_peer_leave(websocket: WebSocket, room_id: str):
    for ws in list(rooms.get(room_id, [])):
        if ws != websocket:
            try:
                await ws.send_json({
                    "type": "leave",
                    "client_id": "peer"
                })
            except Exception as e:
                logger.error(f"[{room_id}] leave 알림 전송 실패: {e}")
                remove_client(ws, room_id)

@router.websocket("/ws/slts/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    if room_id in rooms and len(rooms[room_id]) >= MAX_ROOM_CAPACITY:
        await websocket.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과로 접속 거부됨")
        return

    await websocket.accept()
    logger.info(f"Client가 Room:[{room_id}]에 접속했습니다.")

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                parsed = json.loads(data)
                message_type = parsed.get("type")
                message_data = parsed.get("data")

                if message_type == "hand_data":
                    # 예측 시도
                    try:
                        prediction = ksl_to_korean(message_data["hand_data"])
                        logger.info(f"[{room_id}] 예측 결과: {prediction}")
                    except Exception as e:
                        logger.error(f"[{room_id}] 예측 오류: {e}")
                        prediction = "예측 실패"

                    for ws in list(rooms.get(room_id, [])):
                        try:
                            # 예측 결과 전송
                            await ws.send_json({
                                "type": "text",
                                "client_id": "peer" if ws != websocket else "self",
                                "result": prediction
                            })
                        except Exception as e:
                            logger.error(f"[{room_id}] 클라이언트 전송 오류: {e}")
                            remove_client(ws, room_id)

                elif message_type in ["offer", "answer", "candidate"]:
                    logger.info(f"Room:[{room_id}] - WebRTC 메시지 수신: {message_type}")
                    for ws in list(rooms.get(room_id, [])):
                        if ws != websocket:
                            try:
                                await ws.send_text(json.dumps({
                                    "type": message_type,
                                    "data": message_data
                                }))
                            except Exception as e:
                                logger.error(f"Room:[{room_id}] - WebRTC 시그널 전송 중 오류 발생: {e}")
                                remove_client(ws, room_id)

                elif message_type == "camera_state":
                    for ws in rooms.get(room_id, []):
                        try:
                            await ws.send_json({
                                "type": "camera_state",
                                "client_id": "peer" if ws != websocket else "self",
                                "data": message_data
                            })
                        except Exception as e:
                            logger.error(f"카메라 상태 전송 실패: {e}")
                
                elif message_type == "mic_state":
                    for ws in rooms.get(room_id, []):
                        await ws.send_json({
                            "type": "mic_state",
                            "client_id": "peer" if ws != websocket else "self",
                            "data": message_data
                        })

                else:
                    logger.warning(f"[{room_id}] 지원되지 않는 메시지 타입: {message_type}")

            except Exception as e:
                logger.error(f"[{room_id}] 메시지 파싱 오류: {e}")
                continue

    except WebSocketDisconnect:
        logger.info(f"Client가 Room:[{room_id}]에서 나갔습니다.")
        await notify_peer_leave(websocket, room_id)
        remove_client(websocket, room_id)

    except Exception as e:
        logger.error(f"[{room_id}] WebSocket 처리 오류: {e}")
        await notify_peer_leave(websocket, room_id)
        remove_client(websocket, room_id)