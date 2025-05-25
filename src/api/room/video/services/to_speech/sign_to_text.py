import numpy as np
from collections import deque, Counter
from tensorflow.keras.models import load_model
from core.log.logging import logger

# 모델 및 라벨 로드
model = load_model("src/resources/sign_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)

# 설정값
WINDOW_SIZE = 30
CONFIDENCE_THRESHOLD = 0.7
PREDICTION_HISTORY_SIZE = 10
MIN_CONFIRM_COUNT = 7

HAND_ABSENCE_THRESHOLD = 1e-4
HAND_ABSENCE_FRAME_COUNT = 30  # 1초간 손이 안 보이면 종료

# 상태 저장용 전역 변수
prediction_history = deque(maxlen=PREDICTION_HISTORY_SIZE)
last_landmark = None
hand_absent_counter = 0

def ksl_to_korean(sequence: dict) -> str:
    global last_landmark, hand_absent_counter

    pose = sequence.get('pose', [])
    if len(pose) < WINDOW_SIZE:
        logger.warning(f"[입력 부족] 프레임 수 부족: {len(pose)}프레임")
        return ""

    logger.info(f"[입력 수신] 총 프레임 수: {len(pose)}")

    frames = []
    for idx, frame in enumerate(pose):
        if len(frame) != 75:
            logger.warning(f"[프레임 오류] {idx}번째 프레임이 75개 landmark 아님: {len(frame)}개")
            return ""
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in frame], dtype=np.float32).flatten()
        frames.append(coords)

    frames = np.array(frames, dtype=np.float32)
    word_output = ""

    for i in range(len(frames) - WINDOW_SIZE + 1):
        window = frames[i:i+WINDOW_SIZE]
        pred = model.predict(np.expand_dims(window, axis=0), verbose=0)[0]
        max_idx = int(np.argmax(pred))
        confidence = float(pred[max_idx])
        label = str(class_names[max_idx])

        logger.info(f"[예측] 윈도우 {i} → '{label}' (신뢰도: {confidence:.3f})")

        if confidence >= CONFIDENCE_THRESHOLD:
            prediction_history.append(label)
            logger.debug(f"[누적] '{label}' 예측 추가 → 히스토리: {list(prediction_history)}")
        else:
            logger.debug(f"[무시] 낮은 신뢰도 {confidence:.3f} → 예측 보류")

        current_landmark = window[-1]

        left_hand = current_landmark[33*3 : 54*3]
        right_hand = current_landmark[54*3 : 75*3]

        left_mean = np.mean(np.abs(left_hand))
        right_mean = np.mean(np.abs(right_hand))

        if left_mean < HAND_ABSENCE_THRESHOLD and right_mean < HAND_ABSENCE_THRESHOLD:
            hand_absent_counter += 1
            logger.debug(f"[손 사라짐] frame {i} → {hand_absent_counter}/{HAND_ABSENCE_FRAME_COUNT}")
        else:
            hand_absent_counter = 0

        if hand_absent_counter >= HAND_ABSENCE_FRAME_COUNT:
            counter = Counter(prediction_history)
            if counter:
                best_label, count = counter.most_common(1)[0]
                logger.info(f"[문장 종료 후보] '{best_label}' 등장 {count}회")
                if count >= MIN_CONFIRM_COUNT:
                    logger.info(f"✅ 단어 확정 (손 사라짐 기준): '{best_label}'")
                    word_output = best_label
            prediction_history.clear()
            hand_absent_counter = 0

        last_landmark = current_landmark

    if word_output == "":
        logger.info("📭 최종 예측 없음 (조건 불충족)")
    return word_output