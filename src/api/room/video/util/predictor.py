# src/api/room/video/util/predictor_fsm.py

import numpy as np
from collections import deque, Counter
from tensorflow.keras.models import load_model
from core.log.logging import logger
from src.api.room.video.services.to_speech.text_to_sentence import words_to_sentence
from typing import Optional

class SignPredictorFSM:
    def __init__(self):
        self.model = load_model("src/resources/sign_model.h5")
        self.class_names = np.load("src/resources/class_names.npy", allow_pickle=True)
        self.window_size = 30
        self.conf_threshold = 0.7
        self.no_motion_frame_threshold = 90
        self.low_conf_counter = 0
        self.word_buffer = []
        self.last_word = None

    def normalize_landmarks(self, frame: list) -> np.ndarray:
        coords = np.array([[lm['x'], lm['y'], lm['z']] for lm in frame], dtype=np.float32)

        if coords.shape[0] != 75:
            raise ValueError("landmark 개수가 75개가 아닙니다.")

        # 중심 정렬 기준: nose (0번)
        base = coords[0]
        coords -= base

        # 스케일 정규화 기준: 양 어깨 (11번, 12번)
        left_shoulder = coords[11]
        right_shoulder = coords[12]
        scale = np.linalg.norm(left_shoulder - right_shoulder)
        coords /= (scale + 1e-6)

        return coords.flatten()

    def predict(self, landmark_seq: list) -> Optional[str]:
        if len(landmark_seq) < self.window_size:
            logger.debug("입력 landmark 부족")
            return None

        try:
            frames = [self.normalize_landmarks(frame) for frame in landmark_seq[-self.window_size:]]
        except Exception as e:
            logger.warning(f"[정규화 실패] {e}")
            return None

        window = np.array(frames, dtype=np.float32)
        pred = self.model.predict(np.expand_dims(window, axis=0), verbose=0)[0]
        max_idx = int(np.argmax(pred))
        confidence = float(pred[max_idx])
        label = str(self.class_names[max_idx])

        logger.info(f"[예측] '{label}' (신뢰도: {confidence:.3f})")

        if confidence >= self.conf_threshold:
            self.low_conf_counter = 0
            if label != self.last_word:
                logger.info(f"📌 단어 확정: {label}")
                self.word_buffer.append(label)
                self.last_word = label
        else:
            self.low_conf_counter += 1
            logger.debug(f"[낮은 신뢰도] → 누적 {self.low_conf_counter}/{self.no_motion_frame_threshold}")

        if self.low_conf_counter >= self.no_motion_frame_threshold:
            if self.word_buffer:
                sentence = words_to_sentence(self.word_buffer)
                logger.info(f"📝 문장 완성: {sentence}")
                self.word_buffer.clear()
                self.last_word = None
                self.low_conf_counter = 0
                return sentence
            self.low_conf_counter = 0

        return None
