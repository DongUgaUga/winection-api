from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

# Logging 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# WebSocket 연결을 관리할 방(room) 딕셔너리
rooms = {}

stsl_router = APIRouter()

@stsl_router.websocket("/stsl/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """ STSL WebSocket 서버: 프론트엔드에서 전송한 STT 데이터를 수신 """
    await websocket.accept()
    logging.info(f"STSL WebSocket 연결됨 - Room:[{room_id}]")

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            # WebSocket으로부터 데이터 수신
            data = await websocket.receive_text()
            data_json = json.loads(data)

            if "text" in data_json:
                received_text = data_json["text"]
                logging.info(f"[STT 수신] Room:[{room_id}] - {received_text}")

                # 현재 방에 있는 모든 클라이언트에게 전송 (Broadcast 가능)
                for ws in rooms[room_id]:
                    try:
                        await ws.send_text(json.dumps({"text": received_text}))
                    except Exception as e:
                        logging.error(f"[전송 오류] Room:[{room_id}] - {e}")
                        rooms[room_id].remove(ws)

    except WebSocketDisconnect:
        logging.info(f"STSL WebSocket 연결 종료 - Room:[{room_id}]")
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:  # 방에 아무도 없으면 삭제
            del rooms[room_id]
    except Exception as e:
        logging.error(f"[STSL WebSocket 오류] {e}")