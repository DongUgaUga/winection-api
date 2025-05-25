import numpy as np
from collections import deque, Counter
from tensorflow.keras.models import load_model
from core.log.logging import logger

model = load_model("src/resources/sign_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)

WINDOW_SIZE = 30
CONFIDENCE_THRESHOLD = 0.7
PREDICTION_HISTORY_SIZE = 10
MIN_CONFIRM_COUNT = 7
MOVEMENT_THRESHOLD = 1e-4  # 변화량 기준

prediction_history = deque(maxlen=PREDICTION_HISTORY_SIZE)
last_landmark = None

def calculate_variance(frame, prev_frame):
    diff = frame - prev_frame
    return np.mean(np.square(diff))

def ksl_to_korean(sequence: dict) -> str:
    global last_landmark
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
        if last_landmark is not None:
            variance = calculate_variance(current_landmark, last_landmark)
            logger.debug(f"[변화량] {variance:.8f}")

            if variance < MOVEMENT_THRESHOLD:
                counter = Counter(prediction_history)
                if counter:
                    best_label, count = counter.most_common(1)[0]
                    logger.info(f"[다수결 후보] '{best_label}' 등장 {count}회")
                    if count >= MIN_CONFIRM_COUNT:
                        logger.info(f"✅ 단어 확정: '{best_label}'")
                        word_output = best_label
                    else:
                        logger.info("❌ 확정 실패: 등장 횟수 부족")
                prediction_history.clear()

        last_landmark = current_landmark

    if word_output == "":
        logger.info("📭 최종 예측 없음 (조건 불충족)")
    return word_output
