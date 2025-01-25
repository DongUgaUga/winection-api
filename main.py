from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import mediapipe as mp
import base64
import uuid



app = FastAPI()

# MediaPipe Hands 모델 초기화 (손 인식을 위한 설정)
mp_hands = mp.solutions.hands.Hands(
    static_image_mode=False, max_num_hands=2,
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)

# 방 정보를 저장할 딕셔너리 (각 방의 클라이언트 목록 관리)
rooms = {}


# 손 좌표를 분석하는 함수
def analyze_hand_pose(frame):
    # 이미지 좌우 반전 (거울 효과)
    frame = cv2.flip(frame, 1)

    # MediaPipe를 사용하여 손 인식 수행
    results_hands = mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    hands_info = []
    if results_hands.multi_hand_landmarks:
        for handLms, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
            hand_type = handedness.classification[0].label  # 'Left' or 'Right'
            wrist = handLms.landmark[0]
            hands_info.append([hand_type, round(wrist.x, 2), round(wrist.y, 2), round(wrist.z, 2)])

    return hands_info


# WebSocket 핸들링 (클라이언트 연결 및 데이터 처리)
@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    client_id = str(uuid.uuid4())  # 클라이언트에 고유한 ID 부여
    print(f"Client {client_id} connected to room {room_id}")

    # 방이 존재하지 않으면 새로운 방 생성
    if room_id not in rooms:
        rooms[room_id] = []

    # 방 인원이 2명 초과 시 연결 차단
    if len(rooms[room_id]) >= 2:
        await websocket.send_text("방이 꽉 찼습니다.")
        await websocket.close()
        return

    # 방에 클라이언트 추가
    rooms[room_id].append((client_id, websocket))

    try:
        while True:
            # 클라이언트로부터 영상 프레임 수신
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(',')[1])
            np_arr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            # 손 좌표 분석
            hands_info = analyze_hand_pose(frame)

            # 클라이언트에게 손 정보 전송
            response = {"client_id": client_id, "my_hand_info": hands_info}

            for cid, client in rooms[room_id]:
                if cid != client_id:
                    await client.send_json({"client_id": "peer", "hand_info": hands_info})
                else:
                    await client.send_json({"client_id": "self", "hand_info": hands_info})

    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected from room {room_id}")
        rooms[room_id] = [c for c in rooms[room_id] if c[0] != client_id]
    finally:
        await websocket.close()