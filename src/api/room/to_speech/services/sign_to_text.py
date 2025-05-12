import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
from tensorflow.keras.models import load_model

# 모델 및 클래스 로드
model = load_model("src/resources/sign_model.h5")
class_names = np.load("src/resources/class_names.npy", allow_pickle=True)
from core.log.logging import logger 

def ksl_to_korean(sequence: dict) -> str:
    try:
        pose = sequence.get('pose', [])
        if len(pose) != 30:
            raise ValueError("입력 pose의 길이는 반드시 30프레임이어야 합니다.")

        frames = []
        for frame in pose:
            if len(frame) != 75:
                raise ValueError("각 프레임은 75개의 landmark를 포함해야 합니다.")
            coords = [[lm['x'], lm['y'], lm['z']] for lm in frame]
            frames.append(np.array(coords).flatten())

        arr = np.array(frames).reshape(1, 30, 225).astype(np.float32)
        pred = model.predict(arr, verbose=0)[0]  # (num_classes,)
        max_idx = np.argmax(pred)
        confidence = pred[max_idx]
        label = str(class_names[max_idx])
        
        if confidence < 0.7:
            return ""  # 또는 "신뢰도 낮음" 등
        else :
            logger.info(f"예측 결과: '{label}' (신뢰도: {confidence:.3f})")
            return str(label)

    except Exception as e:
        raise RuntimeError(f"예측 중 오류 발생: {e}")
