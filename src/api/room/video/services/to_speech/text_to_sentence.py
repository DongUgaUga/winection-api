import openai
from core.config.env_config import OPENAI_API_KEY
from core.log.logging import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def text_to_sentence(words: list[str]) -> str:
    if not words:
        return ""

    system_message = {
        "role": "system",
        "content": (
            "너는 수어 통역 결과를 자연스러운 문장으로 바꿔주는 역할이야.\n"
            "내가 주는 입력은 수어에서 추출된 단어들의 나열이야.\n"
            "이 단어들을 이용해 자연스럽고 이해하기 쉬운 **한국어 문장 하나만** 만들어줘.\n"
            "절대 설명이나 해석을 덧붙이지 말고, **결과로는 오직 완성된 문장 하나만 출력**해."
        )
    }

    messages = [system_message, {"role": "user", "content": " ".join(words)}]

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=128,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.exception(f"[OpenAI] API 호출 중 오류 발생: {e}")
        return "문장 생성 실패"
    
def stop_text_to_sentence(words: list[str]) ->str:
        response = "과도한 api의 사용을 막기위해 잠시 기능을 중단했습니다."
        return response