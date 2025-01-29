# Google TTS 음성 변환
import google.cloud.texttospeech as tts
import base64
import os
from dotenv import load_dotenv
import logging

# 환경변수 로드
load_dotenv()

# API 키 설정
GOOGLETTS_API_KEY = os.getenv("GOOGLETTS_API_KEY")
if not GOOGLETTS_API_KEY:
    raise ValueError("환경변수 'GOOGLETTS_API_KEY'가 설정되지 않았습니다.")

# 프로젝트 ID
PROJECT_ID = "winection-project"

def text_to_speech(voice_name: str, text: str) -> str:
    try:
        client = tts.TextToSpeechClient(client_options={"api_key": GOOGLETTS_API_KEY, "quota_project_id": PROJECT_ID})
        language_code = "-".join(voice_name.split("-")[:2])

        # 텍스트 입력 설정
        text_input = tts.SynthesisInput(text=text)

        # 음성 선택 파라미터
        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )

        # 오디오 생성 설정 (MP3 형식)
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

        # TTS 호출
        response = client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        # 오디오 데이터를 Base64로 인코딩하여 반환
        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")

        return audio_base64

    except Exception as e:
        logging.exception(f"[Google TTS] 음성 변환 중 오류 발생: {str(e)}")
        raise RuntimeError(f"Google TTS 음성 변환 중 오류 발생: {str(e)}")