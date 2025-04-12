import numpy as np
from tensorflow.keras.models import load_model
from core.log.logging import logger

# 모델 및 라벨 클래스 로드
model = load_model("src/resources/ksl_cnn_lstm_model.h5")
class_names = np.load("src/resources/class_names.npy")

def ksl_to_korean(sequence: dict) -> str:
    try:
        logger.info(f"입력 데이터 타입: {type(sequence)}")
        
        # 'pose' 데이터 가져오기
        pose = sequence.get('pose', [])
        
        # 각 좌표가 x, y, z인 리스트로 변환
        pose_data = []
        for lm in pose:
            pose_data.append([lm['x'], lm['y'], lm['z']])

        # pose_data가 60x3 shape 이어야 함
        arr = np.array(pose_data, dtype=np.float32)

        # 데이터 크기 확인
        logger.info(f"원본 데이터 크기: {arr.shape}, 데이터 크기: {arr.size}")

        # pose 데이터가 60개 미만이라면 0으로 채워서 (60, 3) 형태로 맞추기
        if arr.shape[0] < 60:
            missing_rows = 60 - arr.shape[0]
            zero_data = np.zeros((missing_rows, 3), dtype=np.float32)
            arr = np.vstack([arr, zero_data])

        # 데이터 크기 확인
        logger.info(f"변경된 데이터 크기: {arr.shape}, 데이터 크기: {arr.size}")

        # 3D 좌표 (x, y, z)마다 75씩 반복하여 (60, 225)로 만들어준다
        try:
            arr_expanded = np.tile(arr, (1, 75))  # (60, 225)로 확장
            arr_expanded = np.reshape(arr_expanded, (1, 60, 225))  # 모델이 요구하는 (1, 60, 225) 형태로 변환
        except Exception as e:
            logger.error(f"reshape 오류 발생: {e}")
            raise RuntimeError(f"reshape 오류 발생: {e}")

        # 데이터 크기 확인
        logger.info(f"reshape 후 데이터 크기: {arr_expanded.shape}, 데이터 크기: {arr_expanded.size}")

        # 모델 입력 형태로 변환 (1, 60, 225)
        input_tensor = arr_expanded
        
        pred = model.predict(input_tensor)
        
        # 예측 결과를 한국어로 변환
        label = class_names[np.argmax(pred)]

        # 예측 결과를 로그로 남기기
        logger.info(f"예측된 결과: {label}")

        return str(label)

    except Exception as e:
        logger.error(f"예측 중 오류 발생: {str(e)}")
        raise RuntimeError(f"예측 중 오류 발생: {str(e)}")