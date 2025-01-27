from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json

app = FastAPI()
rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = []
    rooms[room_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            hand_data = json.loads(data).get("hand_data")

            # 모든 클라이언트에게 손 좌표 전송
            for ws in rooms[room_id]:
                if ws != websocket:
                    await ws.send_json({"client_id": "peer", "hand_info": hand_data})
                else:
                    await ws.send_json({"client_id": "self", "hand_info": hand_data})

    except WebSocketDisconnect:
        rooms[room_id].remove(websocket)
        print("Client disconnected")