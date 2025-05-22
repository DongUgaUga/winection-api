import openai
from core.config.env_config import OPENAI_API_KEY
from core.log.logging import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def words_to_sentence(words: list[str]) -> str:
    """단어 리스트를 한국어 문장으로 변환"""
    if not words:
        return ""

    system_message = {
        "role": "system",
        "content": "내가 주는건 수화를 번역한 단어들의 나열이야. 모든 단어를 합쳐서 자연스러운 한국어 문장으로 변환해. 부가적인 설명 없이 오직 한글로 하나의 문장만 출력해."
    }

    messages = [system_message, {"role": "user", "content": " ".join(words)}]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=128,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f"[OpenAI] API 호출 중 오류 발생: {e}")
        return "문장 생성 실패"
    
def stop_words_to_sentence(words: list[str]) ->str:
        response = "과도한 api의 사용을 막기위해 잠시 기능을 중단했습니다."
        return response