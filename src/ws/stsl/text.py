# 음성 -> 텍스트 변환
import google.cloud.speech as stt
import base64
import logging
from ws.keyload import GOOGLE_API_KEY, PROJECT_ID

def speech_to_text(audio_base64: str) -> str:
    try:
        client = stt.SpeechClient(client_options={"api_key": GOOGLE_API_KEY, "quota_project_id": PROJECT_ID})
        print(audio_base64)
        # Base64 디코딩
        audio_data = base64.b64decode(audio_base64)
        audio = stt.RecognitionAudio(content=audio_data)

        # STT 요청 설정 (한국어)
        config = stt.RecognitionConfig(
            encoding=stt.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="ko-KR"
        )

        # Google STT API 요청
        response = client.recognize(config=config, audio=audio)

        # 변환된 텍스트 반환
        texts = [result.alternatives[0].transcript for result in response.results]
        print("text: " + " ".join(texts))
        return " ".join(texts) if texts else ""

    except Exception as e:
        logging.error(f"STT 변환 중 오류 발생: {e}")
        return "오류 발생"