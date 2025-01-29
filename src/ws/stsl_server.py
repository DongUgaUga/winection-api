from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from ws.stsl.text import speech_to_text  # STT 변환 함수

logging.basicConfig(level=logging.INFO)

stsl_router = APIRouter()

@stsl_router.websocket("/stsl/{room_id}")
async def websocket_stsl_endpoint(websocket: WebSocket, room_id: str):
    try:
        await websocket.accept()
        logging.info(f"STSL WebSocket 연결됨 - Room:[{room_id}]")

        while True:
            try:
                data = await websocket.receive_text()
                data_json = json.loads(data)

                if "audio_base64" in data_json:
                    text_result = speech_to_text(data_json["audio_base64"])
                    await websocket.send_json({"text": text_result})

            except WebSocketDisconnect:
                logging.info(f"Client가 STSL Room:[{room_id}]에서 나갔습니다.")
                break
            except Exception as e:
                logging.error(f"STSL Room:[{room_id}] - 데이터 처리 중 오류 발생: {e}")

    except WebSocketDisconnect:
        logging.info(f"Client가 STSL Room:[{room_id}]에서 나갔습니다.")