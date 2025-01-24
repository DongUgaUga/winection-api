import cv2
import mediapipe as mp
import math
from PIL import Image, ImageDraw, ImageFont
import numpy as np

cap = cv2.VideoCapture(0)

# MediaPipe Hands와 Pose 모델 초기화
mpHands = mp.solutions.hands
mpPose = mp.solutions.pose
my_hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
my_pose = mpPose.Pose()

# 손목과 손끝의 거리 계산 함수
def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

# 손과 팔 위치 인식
compareIndex = [[18, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
open = [False, False, False, False, False]  # 손가락 접힘 유무 파악
gesture = [[True, True, True, True, True, "Hi"],
           [False, True, True, False, False, "Yeah!"],
           [True, False, False, False, False, "Good"],
           [False, False, True, False, False, "Fuck"]]

# 원하는 출력 크기
output_width = 1280
output_height = 768

# 한글 폰트 경로 설정 (적절한 TTF 파일 경로로 수정)
font_path = "Pretendard.ttf"  # 맑은 고딕 예시
font_size = 32
font = ImageFont.truetype(font_path, font_size)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)  # 좌우 반전
    h, w, c = img.shape
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Pose 모델로 사람의 자세 추적
    results_pose = my_pose.process(imgRGB)

    # Hands 모델로 손 추적
    results_hands = my_hands.process(imgRGB)

    if results_hands.multi_hand_landmarks:
        for handLms, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
            # 손의 종류 확인 (왼손, 오른손)
            hand_type = handedness.classification[0].label  # 'Left' or 'Right'

            # 손목 좌표 가져오기 (손목은 landmark[0]에 위치)
            wrist_x = handLms.landmark[0].x
            wrist_y = handLms.landmark[0].y
            wrist_z = handLms.landmark[0].z

            # 엄지 손가락 제일 낮은 관절 좌표 가져오기 (엄지의 제일 낮은 관절은 landmark[2]에 위치)
            thumb_base_x = handLms.landmark[2].x
            thumb_base_y = handLms.landmark[2].y
            thumb_base_z = handLms.landmark[2].z

            # 손목과 엄지 위치를 기준으로 손의 앞/뒤를 구별
            if ((thumb_base_x > wrist_x) and (hand_type == 'Right')) or ((thumb_base_x < wrist_x) and (hand_type == 'Left')):
                hand_side = "손등"  # 손이 카메라를 향하고 있을 때
            else:
                hand_side = "손바닥"  # 손이 반대 방향을 향하고 있을 때

            # 손목과 손끝의 3D 좌표 기반으로 텍스트 출력
            text_x = int(wrist_x * w)
            text_y = int(wrist_y * h)

            # 손이 어느 방향을 향하고 있는지 출력
            pil_img = Image.fromarray(img)
            draw = ImageDraw.Draw(pil_img)

            # 한글 텍스트 추가
            draw.text((round(text_x) - 50, round(text_y) - 250), f"{hand_type} - {hand_side}", font=font,
                      fill=(0, 255, 0))

            # 다시 OpenCV 형식으로 변환
            img = np.array(pil_img)

            for t in range(0, len(gesture)):
                flag = True
                for j in range(0, 5):
                    if gesture[t][j] != open[j]:
                        flag = False
                if flag:
                    # 제스처 텍스트를 그대로 출력
                    draw.text((round(text_x) - 50, round(text_y) - 300), gesture[t][5], font=font, fill=(0, 0, 0))
                    print(gesture[t][5])

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    if results_pose.pose_landmarks:
        # 팔꿈치, 어깨 등 위치 추적
        for landmark in results_pose.pose_landmarks.landmark:
            # 팔꿈치, 어깨 등의 위치 추적하기 (예시로 어깨와 팔꿈치)
            if landmark.visibility > 0.5:  # 점이 보이는 정도가 50% 이상일 때만 표시
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(img, (x, y), 10, (255, 0, 0), -1)  # 팔꿈치와 어깨에 원 표시

        # 어깨와 팔꿈치 연결 선 그리기
        if results_pose.pose_landmarks:
            mpDraw.draw_landmarks(img, results_pose.pose_landmarks, mpPose.POSE_CONNECTIONS)

    # 영상 출력
    cv2.imshow("Hand and Pose Tracking", img)
    if cv2.waitKey(1) == ord("q"):  # q 누를 시 웹캠 종료
        break

cap.release()
cv2.destroyAllWindows()