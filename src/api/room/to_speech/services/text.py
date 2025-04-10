# text.py

import numpy as np
from tensorflow.keras.models import load_model

# 모델 & 클래스명 로드
model = load_model("src/resources/ksl_cnn_lstm_model.h5")
class_names = np.load("src/resources/class_names.npy")

def ksl_to_korean(sequence: list[list[float]]) -> str:
    try:
        arr = np.array(sequence, dtype=np.float32)
        if arr.shape != (60, 225):
            raise ValueError("입력 shape은 (60, 225) 여야 합니다.")

        input_tensor = np.expand_dims(arr, axis=0)  # (1, 60, 225)
        pred = model.predict(input_tensor)
        label = class_names[np.argmax(pred)]

        return str(label)

    except Exception as e:
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")