import numpy as np
from tensorflow.keras.models import load_model

# 모델 및 라벨 클래스 로드
model = load_model("src/resources/ksl_cnn_lstm_model.h5")
class_names = np.load("src/resources/class_names.npy")

def ksl_to_korean(sequence: list[list[float]]) -> str:
    try:
        print(f"입력 데이터 타입: {type(sequence)}")
        if isinstance(sequence, dict):
            print(f"입력된 dict 형태의 데이터: {sequence}")
            sequence = sequence.get('land_mark', [])
        
        if not isinstance(sequence, list):
            raise ValueError("입력 데이터는 list 형태여야 합니다.")

        arr = np.array(sequence, dtype=np.float32)

        # 각 좌표는 (60, 3) 형태로 되어 있음. 이를 (60, 225)로 맞춰야 함.
        if arr.shape != (60, 3):
            raise ValueError("입력 shape은 (60, 3) 여야 합니다.")

        # 각 좌표의 x, y, z 값을 하나로 합쳐서 225에 맞게 변환
        arr = arr.flatten()  # (60, 3) → (180,)
        
        # 부족한 부분을 0으로 패딩하여 (225,) 크기로 맞추기
        padding = np.zeros(225 - arr.shape[0])  # 225 크기에 맞는 패딩 추가
        arr = np.concatenate([arr, padding])  # (180,) → (225,)

        # 모델 입력을 위한 차원 확장
        input_tensor = np.expand_dims(arr, axis=0)  # (225,) → (1, 225)
        pred = model.predict(input_tensor)
        
        label = class_names[np.argmax(pred)]

        return str(label)

    except Exception as e:
        print(f"예측 중 오류 발생: {str(e)}")
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")