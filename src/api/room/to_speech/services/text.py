from tensorflow.keras.models import load_model
import numpy as np

model = load_model("ksl_cnn_lstm_model.h5")
class_names = np.load("class_names.npy")

def ksl_to_korean(sequence: list[list[float]]) -> str:
    try:
        arr = np.array(sequence, dtype=np.float32)

        if arr.shape != (60, 225):
            raise ValueError(f"입력 shape은 (60, 225) 여야 합니다. 입력 shape: {arr.shape}")

        input_tensor = np.expand_dims(arr, axis=0)  # (1, 60, 225)

        pred = model.predict(input_tensor)

        label = class_names[np.argmax(pred)]

        return str(label)

    except Exception as e:
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")