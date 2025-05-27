import google.cloud.texttospeech as tts
import base64
import os
from dotenv import load_dotenv
from core.log.logging import logger
from core.config.env_config import GOOGLE_API_KEY, PROJECT_ID

VOICE_MAP = {
    "성인 남자": "ko-KR-Standard-C",
    "성인 여자": "ko-KR-Chirp3-HD-Erinome",
    "어린 남자": "ko-KR-Chirp3-HD-Orus",
    "어린 여자": "ko-KR-Wavenet-A",
}

def get_voice_name(label: str) -> str:
    return VOICE_MAP.get(label, "ko-KR-Standard-C")

def sentence_to_speech(voice_name: str, text: str) -> str:
    try:
        client = tts.TextToSpeechClient(client_options={"api_key": GOOGLE_API_KEY, "quota_project_id": PROJECT_ID})
        language_code = "-".join(voice_name.split("-")[:2])

        text_input = tts.SynthesisInput(text=text)

        voice_params = tts.VoiceSelectionParams(
            language_code=language_code, name=voice_name
        )

        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

        response = client.synthesize_speech(
            input=text_input,
            voice=voice_params,
            audio_config=audio_config,
        )

        audio_base64 = base64.b64encode(response.audio_content).decode("utf-8")

        return audio_base64

    except Exception as e:
        logger.exception(f"[Google TTS] 음성 변환 중 오류 발생: {str(e)}")
        raise RuntimeError(f"Google TTS 음성 변환 중 오류 발생: {str(e)}")
