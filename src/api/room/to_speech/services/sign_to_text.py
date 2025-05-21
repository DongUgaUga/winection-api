import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
from tensorflow.keras.models import load_model
from core.log.logging import logger 

# 모델 및 클래스 로드
model = load_model("src/resources/sign_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)

# 슬라이딩 윈도우 설정
WINDOW_SIZE = 30
STRIDE = 5
CONFIDENCE_THRESHOLD = 0.7

def ksl_to_korean(sequence: dict) -> str:
    try:
        pose = sequence.get('pose', [])
        if len(pose) < WINDOW_SIZE:
            raise ValueError("입력 pose의 길이는 최소 30프레임 이상이어야 합니다.")

        # landmark 변환: (N, 75) → (N, 225)
        frames = []
        for frame in pose:
            if len(frame) != 75:
                raise ValueError("각 프레임은 75개의 landmark를 포함해야 합니다.")
            coords = [[lm['x'], lm['y'], lm['z']] for lm in frame]
            frames.append(np.array(coords).flatten())

        frames = np.array(frames, dtype=np.float32)  # (N, 225)

        # 슬라이딩 윈도우 기반 예측
        preds = []
        for start in range(0, len(frames) - WINDOW_SIZE + 1, STRIDE):
            window = frames[start:start + WINDOW_SIZE]
            if window.shape == (WINDOW_SIZE, 225):
                pred = model.predict(np.expand_dims(window, axis=0), verbose=0)[0]
                preds.append(pred)

        if not preds:
            raise RuntimeError("예측할 슬라이딩 윈도우가 없습니다.")

        avg_pred = np.mean(preds, axis=0)  # (num_classes,)
        max_idx = np.argmax(avg_pred)
        confidence = avg_pred[max_idx]
        label = str(class_names[max_idx])

        if confidence < CONFIDENCE_THRESHOLD:
            return ""
        else:
            logger.info(f"예측 결과: '{label}' (신뢰도: {confidence:.3f})")
            return label

    except Exception as e:
        raise RuntimeError(f"예측 중 오류 발생: {e}")
