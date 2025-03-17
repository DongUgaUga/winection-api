from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.models import WebSocketMessage
import json
from core.logging import logger
from api.services.stsl.word import text_to_word

# WebSocket 연결을 관리할 방(room) 딕셔너리
rooms = {}

stsl_router = APIRouter()

@stsl_router.websocket("/api/stsl/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    logger.info(f"STSL WebSocket 연결됨 - Room:[{room_id}]")

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            # WebSocket으로부터 데이터 수신
            data = await websocket.receive_text()
            try:
                message = WebSocketMessage.parse_raw(data)
            except Exception as e:
                logger.error(f"Room:[{room_id}] - 잘못된 WebSocket 메시지 수신: {e}")
                continue  # 잘못된 데이터 무시

            if message.type == "text":
                received_text = str(message.data.get("text", ""))
                logger.info(f"[STT 수신] Room:[{room_id}] - {received_text}")

                word_list = text_to_word(received_text)
                logger.info(f"[변환된 단어] Room:[{room_id}] - {word_list}")
                
                # 현재 방에 있는 모든 클라이언트에게 전송 (Broadcast 가능)
                for ws in list(rooms.get(room_id, [])):
                    try:
                        await ws.send_text(json.dumps({"text": received_text}))
                    except Exception as e:
                        logger.error(f"Room:[{room_id}] - WebSocket 전송 오류 발생: {e}")
                        rooms[room_id].remove(ws)

    except WebSocketDisconnect:
        logger.info(f"STSL WebSocket 연결 종료 - Room:[{room_id}]")
        if websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
    except Exception as e:
        logger.error(f"[STSL WebSocket 오류] {e}")
