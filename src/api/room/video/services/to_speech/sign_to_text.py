import numpy as np
from dataclasses import dataclass
from collections import Counter, deque
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity
from core.log.logging import logger
from tensorflow.keras.models import load_model, Model

# ✅ 모델 및 임베딩 레이어 준비
base_model = load_model("src/resources/sign_model2_func.h5")
dummy_input = np.zeros((1, 30, 225), dtype=np.float32)
base_model.predict(dummy_input)  # build 강제 수행

intermediate_model = Model(
    inputs=base_model.input,
    outputs=base_model.get_layer("embedding").output
)

# ✅ 클래스 정보 로드
class_names = np.load("src/resources/class_names2.npy", allow_pickle=True)
class_embeddings = np.load("src/resources/class_embeddings.npy")
num_classes = len(class_names)

# ✅ 설정값
WINDOW_SIZE = 30
DISTANCE_THRESHOLD = 0.3
MISSING_HAND_FRAME_THRESHOLD = 7
PERSIST_THRESHOLD = 2
TOP_K = 5
HISTORY_SIZE = 10

# ✅ 무의미한 단어 블랙리스트
BLACKLIST_WORDS = {"왼쪽-눈", "왼쪽-귀"}

@dataclass
class SignPredictorState:
    label_history: deque = deque(maxlen=HISTORY_SIZE)
    missing_hand_counter: int = 0
    last_label: Optional[str] = None
    confirmed_words: list = None

    def __post_init__(self):
        self.confirmed_words = []

def normalize_landmarks(frame: list[dict]) -> np.ndarray:
    if len(frame) != 75:
        raise ValueError("landmark 개수가 75개가 아니다.")
    coords = np.array([[lm["x"], lm["y"], lm["z"]] for lm in frame], dtype=np.float32)
    return coords.flatten()

def is_hand_missing(frame: np.ndarray) -> bool:
    left_hand = frame[33*3 : 54*3]
    right_hand = frame[54*3 : 75*3]
    return np.allclose(left_hand, 0.0) and np.allclose(right_hand, 0.0)

def sign_to_text(sequence: dict, state: SignPredictorState) -> list[str]:
    pose = sequence.get("pose", [])
    if len(pose) < WINDOW_SIZE:
        return []

    try:
        frames = [normalize_landmarks(frame) for frame in pose[-WINDOW_SIZE:]]
    except Exception as e:
        logger.warning(f"[정규화 실패] {e}")
        return []

    # ✅ 손 사라짐 감지
    latest_frame = frames[-1]
    if is_hand_missing(latest_frame):
        state.missing_hand_counter += 1
        # logger.info(f"🖐 손 사라짐 카운터: {state.missing_hand_counter}")
        if state.missing_hand_counter >= MISSING_HAND_FRAME_THRESHOLD:
            result = state.confirmed_words.copy()
            if result:
                logger.info(f"문장 종료 - 누적 단어: {result}")
            state.confirmed_words.clear()
            state.label_history.clear()
            state.last_label = None
            state.missing_hand_counter = 0
            return result
        return []  # 손이 안 보이면 예측 자체 중단
    else:
        state.missing_hand_counter = 0

    # ✅ 예측 수행
    input_tensor = np.array(frames, dtype=np.float32).reshape(1, WINDOW_SIZE, -1)
    embedding = intermediate_model.predict(input_tensor, verbose=0)[0]
    similarities = cosine_similarity([embedding], class_embeddings)[0]

    top_indices = similarities.argsort()[-TOP_K:][::-1]
    top_labels = [(class_names[i], float(similarities[i])) for i in top_indices]
    top_label, top_score = top_labels[0]

    # ✅ 블랙리스트 필터링
    if top_label in BLACKLIST_WORDS:
        return []

    if top_score >= 1 - DISTANCE_THRESHOLD:
        state.label_history.append(top_label)

    if len(state.label_history) >= PERSIST_THRESHOLD:
        most_common, count = Counter(state.label_history).most_common(1)[0]
        if count >= PERSIST_THRESHOLD and most_common != state.last_label:
            logger.info(f"단어: {most_common} (최근 {count}회 반복)")
            state.confirmed_words.append(most_common)
            state.last_label = most_common
            state.label_history.clear()

    return []
