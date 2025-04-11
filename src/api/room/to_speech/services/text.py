import numpy as np
from tensorflow.keras.models import load_model

# 모델 및 라벨 클래스 로드
model = load_model("src/resources/ksl_cnn_lstm_model.h5")
class_names = np.load("src/resources/class_names.npy")

def ksl_to_korean(sequence: dict) -> str:
    try:
        print(f"입력 데이터 타입: {type(sequence)}")
        
        # 'pose' 데이터 가져오기
        pose = sequence.get('pose', [])
        
        # 각 좌표가 x, y, z인 리스트로 변환
        pose_data = []
        for lm in pose:
            pose_data.append([lm['x'], lm['y'], lm['z']])
        
        # pose_data가 60x3 shape 이어야 함
        arr = np.array(pose_data, dtype=np.float32)

        # 모델 입력 형태로 변환 (60, 225)
        if arr.shape != (60, 3):
            raise ValueError(f"입력 shape은 (60, 3) 여야 합니다. 현재 shape: {arr.shape}")
        
        # 모델 예측을 위한 데이터 변환
        input_tensor = np.expand_dims(arr, axis=0)
        pred = model.predict(input_tensor)
        
        # 예측 결과를 한국어로 변환
        label = class_names[np.argmax(pred)]

        return str(label)

    except Exception as e:
        print(f"예측 중 오류 발생: {str(e)}")
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")