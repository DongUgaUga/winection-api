import cv2
import mediapipe as mp
import math
import pyttsx3
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import threading

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
my_hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# TTS 엔진 초기화
engine = pyttsx3.init()

def dist(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1 - x2, 2)) + math.sqrt(math.pow(y1 - y2, 2))

compareIndex = [[18, 4], [6, 8], [10, 12], [14, 16], [18, 20]]
open = [False, False, False, False, False]  # 손가락 접힘 유무 파악
gesture = [[True, True, True, True, True, "안녕하세요"],
           [False, True, True, False, False, "브이"],
           [True, False, False, False, False, "따봉"],
           [False, False, True, False, False, "엿이나 먹어라"]]

# 원하는 출력 크기
output_width = 1280
output_height = 768

# 한글 폰트 경로 설정 (적절한 TTF 파일 경로로 수정)
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 예시
font_size = 32

def speak(text):
    """음성을 출력하는 쓰레드 함수"""
    engine.say(text)
    engine.runAndWait()  # 대기하여 소리가 출력될 때까지 기다림

while True:
    success, img = cap.read()

    img = cv2.flip(img, 1)  # 웹캠과 화면에 맞게 좌우 반전
    img = cv2.resize(img, (output_width, output_height))  # 이미지 크기 조정
    h, w, c = img.shape
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = my_hands.process(imgRGB)

    if results.multi_hand_landmarks:  # 각 손가락의 상태 확인
        for handLms in results.multi_hand_landmarks:
            for i in range(0, 5):
                open[i] = (dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][0]].x,
                                handLms.landmark[compareIndex[i][0]].y) <
                           dist(handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[compareIndex[i][1]].x,
                                handLms.landmark[compareIndex[i][1]].y))
            text_x = (handLms.landmark[0].x * w)
            text_y = (handLms.landmark[0].y * h)
            for t in range(0, len(gesture)):
                flag = True
                for j in range(0, 5):
                    if gesture[t][j] != open[j]:
                        flag = False
                if flag:
                    # Pillow를 사용하여 한글 텍스트 추가
                    pil_img = Image.fromarray(img)  # OpenCV 이미지를 Pillow 이미지로 변환
                    draw = ImageDraw.Draw(pil_img)
                    font = ImageFont.truetype(font_path, font_size)  # 폰트 설정

                    # 텍스트 위치 및 색상 설정
                    draw.text((round(text_x) - 50, round(text_y) - 250), gesture[t][5], font=font, fill=(0, 0, 0))

                    # 다시 OpenCV 형식으로 변환
                    img = np.array(pil_img)

                    print(gesture[t][5])

                    # 음성을 출력하는 쓰레드 생성 및 시작
                    thread = threading.Thread(target=speak, args=(gesture[t][5],))
                    thread.start()

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cv2.imshow("HandTracking", img)
    if cv2.waitKey(1) == ord("q"):  # q 누를 시 웹켐 종료
        break

cap.release()
cv2.destroyAllWindows()
