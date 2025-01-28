from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
import logging
import asyncio

# Logging 설정
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI: 애플리케이션 초기화
app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.1"
)

# WebSocket: 방 정보를 저장하는 딕셔너리
rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    try:
        # WebSocket: 연결 수락
        await websocket.accept()
        print(f"INFO: Client가 Room:[{room_id}]에 접속했습니다.")

        # 방에 클라이언트 추가
        if room_id not in rooms:
            rooms[room_id] = []
        rooms[room_id].append(websocket)

        while True:
            try:
                # WebSocket: 데이터 수신
                data = await websocket.receive_text()
                try:
                    data_json = json.loads(data)
                except json.JSONDecodeError:
                    logging.error(f"Room:[{room_id}] - 잘못된 JSON 형식 데이터 수신")
                    continue

                # WebRTC: 시그널링 데이터 처리
                if "offer" in data_json or "answer" in data_json or "candidate" in data_json:
                    for ws in list(rooms[room_id]):  # 안전한 복사를 위해 리스트로 변환
                        if ws != websocket:
                            try:
                                await ws.send_text(json.dumps(data_json))
                            except Exception as e:
                                logging.error(f"Room:[{room_id}] - WebRTC 시그널 전송 중 오류 발생: {e}")
                                if "WebSocket is not connected." in str(e):
                                    await websocket.accept()

                # 손 좌표 데이터 처리
                elif "hand_data" in data_json:
                    for ws in list(rooms[room_id]):
                        try:
                            if ws != websocket:
                                await ws.send_json({"client_id": "peer", "hand_data": data_json["hand_data"]})
                            else:
                                await ws.send_json({"client_id": "self", "hand_data": data_json["hand_data"]})
                        except Exception as e:
                            logging.error(f"Room:[{room_id}] - 손 좌표 데이터 전송 중 오류 발생: {e}")
                            if "WebSocket is not connected." in str(e):
                                await websocket.accept()

            except WebSocketDisconnect:
                logging.info(f"Client가 Room:[{room_id}]에서 나갔습니다.")
                if websocket in rooms.get(room_id, []):
                    rooms[room_id].remove(websocket)
                    if not rooms[room_id]:
                        del rooms[room_id]
                break
            except Exception as e:
                logging.error(f"Room:[{room_id}] - 데이터 처리 중 오류 발생: {e}")
                if "WebSocket is not connected." in str(e):
                    await websocket.accept()

    except WebSocketDisconnect:
        print(f"INFO: Client가 Room:[{room_id}]에서 나갔습니다.")
        if websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)
        if not rooms.get(room_id):
            del rooms[room_id]
    except Exception as e:
        logging.error(f"WebSocket 연결 처리 중 오류 발생: {e}")
        rooms[room_id].remove(websocket)
        if not rooms[room_id]:
            del rooms[room_id]