from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.models import WebSocketMessage
import json
from core.logging import logger

to_speech_router = APIRouter()
rooms = {}

@to_speech_router.websocket("/ws/slts/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
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
                    # 실시간 손 좌표 중계
                    for ws in list(rooms.get(room_id, [])):
                        try:
                            await ws.send_json({
                                "client_id": "peer" if ws != websocket else "self",
                                "hand_data": message_data
                            })
                        except Exception as e:
                            logger.error(f"[{room_id}] 클라이언트 전송 오류: {e}")
                            rooms[room_id].remove(ws)

            except Exception as e:
                logger.error(f"[{room_id}] 메시지 파싱 오류: {e}")
    except WebSocketDisconnect:
        logger.info(f"Client가 Room:[{room_id}]에서 나갔습니다.")
        if websocket in rooms[room_id]:
            rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
    except Exception as e:
        logger.error(f"[{room_id}] WebSocket 처리 오류: {e}")
        if websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
