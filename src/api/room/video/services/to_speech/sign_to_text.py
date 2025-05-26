import numpy as np
from tensorflow.keras.models import load_model
from core.log.logging import logger
from src.api.room.video.services.to_speech.text_to_sentence import text_to_sentence

model = load_model("src/resources/sign_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)

WINDOW_SIZE = 30
CONFIDENCE_THRESHOLD = 0.7
NO_MOTION_FRAME_THRESHOLD = 90

low_conf_counter = 0
word_buffer = []
last_word = None

def normalize_landmarks(frame: list[dict]) -> np.ndarray:
    coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in frame], dtype=np.float32)
    if coords.shape[0] != 75:
        raise ValueError("landmark 개수가 75개가 아닙니다.")
    base = coords[0]
    coords -= base
    scale = np.linalg.norm(coords[11] - coords[12])
    coords /= (scale + 1e-6)
    return coords.flatten()

def sign_to_text(sequence: dict) -> str:
    global low_conf_counter, word_buffer, last_word

    pose = sequence.get('pose', [])
    if len(pose) < WINDOW_SIZE:
        logger.warning(f"[입력 부족] 프레임 수 부족: {len(pose)}프레임")
        return ""

    try:
        frames = [normalize_landmarks(frame) for frame in pose[-WINDOW_SIZE:]]
    except Exception as e:
        logger.warning(f"[정규화 실패] {e}")
        return ""

    input_tensor = np.array(frames, dtype=np.float32).reshape(1, WINDOW_SIZE, -1)
    pred = model.predict(input_tensor, verbose=0)[0]
    max_idx = int(np.argmax(pred))
    confidence = float(pred[max_idx])
    label = str(class_names[max_idx])

    logger.info(f"[예측] {label} (신뢰도: {confidence:.3f})")

    if confidence >= CONFIDENCE_THRESHOLD:
        low_conf_counter = 0
        if label != last_word:
            logger.info(f"📌 단어 확정: {label}")
            word_buffer.append(label)
            last_word = label
    else:
        low_conf_counter += 1

    if low_conf_counter >= NO_MOTION_FRAME_THRESHOLD:
        if word_buffer:
            sentence = text_to_sentence(word_buffer)
            logger.info(f"📝 문장 완성: {sentence}")
            word_buffer.clear()
            last_word = None
            low_conf_counter = 0
            return sentence
        low_conf_counter = 0

    return ""