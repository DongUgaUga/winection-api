import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
from tensorflow.keras.models import load_model

# 모델 및 라벨 클래스 로드
model = load_model("src/resources/ksl_cnn_lstm_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)

def ksl_to_korean(sequence: dict) -> str:
    try:
        pose = sequence.get('pose', [])
        arr = np.array([[lm['x'], lm['y'], lm['z']] for lm in pose], dtype=np.float32)

        # 길이 맞추기
        if arr.shape[0] < 60:
            pad = np.zeros((60 - arr.shape[0], 3), dtype=np.float32)
            arr = np.vstack([arr, pad])

        # (1,60,225) 형태로 변환
        arr_expanded = np.tile(arr, (1, 75)).reshape((1, 60, 225))

        # verbose=0 으로 프로그레스바 억제
        pred = model.predict(arr_expanded, verbose=0)

        label = class_names[np.argmax(pred)]
        return str(label)

    except Exception as e:
        raise RuntimeError(f"예측 중 오류 발생: {e}")
