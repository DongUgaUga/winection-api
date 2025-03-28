import openai
import os
from dotenv import load_dotenv
from core.logging import logger
from core.config import OPENAI_API_KEY 

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def word_to_sentence(words: list) -> str:
    system_message = {
        "role": "system",
        "content": "너는 이제부터 수화를 번역할 거야. 내가 단어들을 던져주면 그것을 자연스러운 한국어 문장으로 변환해. 부가적인 설명 없이 오직 하나의 문장만 출력해."
    }

    messages = [system_message, {"role": "user", "content": " ".join(words)}]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=128,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.exception(f"[OpenAI] API 호출 중 오류 발생: {str(e)}")
        raise RuntimeError(f"OpenAI API 호출 중 오류 발생: {str(e)}")
    
def stop_word_to_sentence(words: list) ->str:
        response = "과도한 api의 사용을 막기위해 잠시 기능을 중단했습니다."
        return response