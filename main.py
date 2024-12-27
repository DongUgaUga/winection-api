import asyncio
import websockets
import cv2
import mediapipe as mp
import numpy as np
import base64

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

async def process_video(websocket, path):
    try:
        async for message in websocket:
            # 영상 데이터 디코딩
            img_data = base64.b64decode(message)
            img_array = np.frombuffer(img_data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                print("[Python 서버] 디코딩된 이미지가 None입니다.")
                continue

            # Mediapipe 손 추적
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 내 손 추적 데이터 전송
            _, buffer_my = cv2.imencode('.jpg', frame)
            base64_my_frame = base64.b64encode(buffer_my).decode('utf-8')
            await websocket.send(f"myProcessedFrame|{base64_my_frame}")

            # 상대방 데이터가 있을 때만 전송
            if "peer_frame_placeholder" in message:  # 상대방 데이터 조건
                peer_frame = cv2.flip(frame, 1)  # 좌우 반전된 프레임
                _, buffer_peer = cv2.imencode('.jpg', peer_frame)
                base64_peer_frame = base64.b64encode(buffer_peer).decode('utf-8')
                await websocket.send(f"peerProcessedFrame|{base64_peer_frame}")

    except websockets.ConnectionClosed:
        print("[Python 서버] WebSocket 연결 종료됨")

async def main():
    print("WebSocket 서버가 8081 포트에서 실행 중입니다.")
    async with websockets.serve(process_video, "127.0.0.1", 8081):
        await asyncio.Future()  # 서버를 무기한 실행 상태로 유지

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("서버가 수동으로 종료되었습니다.")
