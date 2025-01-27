from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI(
    title="Winection API",
    description="1:1 수어 번역 화상채팅 API",
    version="0.1"
)

# 방 정보를 저장할 딕셔너리 (각 방의 클라이언트 목록 관리)
rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """
    WebSocket 연결을 통해 클라이언트가 손 인식 데이터를 주고받을 수 있습니다.
    
    - **room_id**: 방 ID입니다.
    - 클라이언트가 연결되면 손 좌표 데이터를 주고받습니다.
    - 연결이 끊기면 클라이언트가 자동으로 제거됩니다.
    """
    await websocket.accept()
    print(f"Client connected to room {room_id}")

    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            data_json = json.loads(data)

            # WebRTC signaling (offer/answer/candidate 전달)
            if "offer" in data_json or "answer" in data_json or "candidate" in data_json:
                for ws in rooms[room_id]:
                    if ws != websocket:
                        await ws.send_text(json.dumps(data_json))

            # 손 좌표 데이터 처리
            elif "hand_data" in data_json:
                for ws in rooms[room_id]:
                    if ws != websocket:
                        await ws.send_json({"client_id": "peer", "hand_data": data_json["hand_data"]})
                        print(f"Sent to peer: {data_json['hand_data']}")
                    else:
                        await ws.send_json({"client_id": "self", "hand_data": data_json["hand_data"]})
                        print(f"Sent to self: {data_json['hand_data']}")

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        print(f"Client disconnected from room {room_id}")
