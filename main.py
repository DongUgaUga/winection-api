from fastapi import FastAPI, WebSocket
import cv2
import numpy as np
import mediapipe as mp
import base64

app = FastAPI()

# MediaPipe Hands 및 Pose 모델 초기화
mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_pose = mp.solutions.pose.Pose()

def analyze_hand_pose(frame):
    frame = cv2.flip(frame, 1)
    results_hands = mp_hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    results_pose = mp_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    hands_info = []

    if results_hands.multi_hand_landmarks:
        for handLms, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
            hand_type = handedness.classification[0].label  # 'Left' or 'Right'

            wrist = handLms.landmark[0]
            thumb_base = handLms.landmark[2]

            # 손바닥과 손등 판별
            if ((thumb_base.x > wrist.x and hand_type == 'Right') or
                    (thumb_base.x < wrist.x and hand_type == 'Left')):
                hand_side = "손등"
            else:
                hand_side = "손바닥"

            hands_info.append({
                "hand": hand_type,
                "side": hand_side,
            })

    return hands_info

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    try:
        while True:
            data = await websocket.receive_text()
            image_data = base64.b64decode(data.split(',')[1])
            np_arr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            hands_info = analyze_hand_pose(frame)

            await websocket.send_json({"hands": hands_info})
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        await websocket.close()
        print("Client disconnected")
