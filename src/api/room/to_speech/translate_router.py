from fastapi import APIRouter, HTTPException
from core.schemas.room_schema import TranslationRequest, TranslationResponse
from src.api.room.to_speech.services.sentence import stop_word_to_sentence
from src.api.room.to_speech.services.speech import text_to_speech
from core.log.logging import logger

router = APIRouter()

@router.post(
    "/translate",
    response_model=TranslationResponse,
    responses={
        200: {
            "description": "번역 및 음성 변환 성공",
            "content": {
                "application/json": {
                    "example": {
                        "translated_sentence": "나는 학교에 간다.",
                        "audio_base64": "UklGRjQAAABXQVZFZm10IBAAAAABAAEA..."
                    }
                }
            }
        },
        500: {
            "description": "번역 처리 중 서버 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "sentence_builder 중 오류 발생"}
                }
            }
        }
    }
)
async def word_to_speech(request: TranslationRequest):
    try:
        logger.info("🔍 번역 요청 수신: %s", request.words)

        sentence = stop_word_to_sentence(request.words)
        audio_base64 = text_to_speech("ko-KR-Wavenet-D", sentence)

        return TranslationResponse(translated_sentence=sentence, audio_base64=audio_base64)

    except RuntimeError as e:
        logger.error(f"[sentence_builder] 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail="sentence_builder 중 오류 발생")