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

        # pose 데이터가 33개라면 나머지 27개를 0으로 채워서 (60, 3) 형태로 맞추기
        if arr.shape[0] < 60:
            missing_rows = 60 - arr.shape[0]
            zero_data = np.zeros((missing_rows, 3), dtype=np.float32)
            arr = np.vstack([arr, zero_data])

        # 만약 3개의 특징을 225로 맞추려면 flatten 하거나 확장해야 함
        arr = arr.flatten()  # (180,) 형태로 만듦
        if arr.shape[0] < 225:
            # 225개로 맞추기 위해 0으로 채우기
            arr = np.pad(arr, (0, 225 - arr.shape[0]), 'constant')

        # 모델 입력 형태로 변환 (1, 225)
        input_tensor = np.expand_dims(arr, axis=0)  # (1, 225)
        
        pred = model.predict(input_tensor)
        
        # 예측 결과를 한국어로 변환
        label = class_names[np.argmax(pred)]

        return str(label)

    except Exception as e:
        print(f"예측 중 오류 발생: {str(e)}")
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")