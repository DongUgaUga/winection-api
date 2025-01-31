from openai import OpenAI
import os
from dotenv import load_dotenv
import logging
from ws.keyload import DEEPSEEK_API_KEY


# DeepSeek API 호출 함수
def word_to_sentence(words: list) -> str:
    system_message = {
        "role": "system",
        "content": "너는 이제부터 수화를 번역할 거야. 내가 단어들을 던져주면 그걸 자연스러운 하나의 문장으로 만들어줘. 부가적인 설명은 하지 말고, 오로지 하나의 문장만 출력해."
    }

    messages = [system_message, {"role": "user", "content": " ".join(words)}]

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=1024,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.exception(f"[DeepSeek] API 호출 중 오류 발생: {str(e)}")
        raise RuntimeError(f"DeepSeek API 호출 중 오류 발생: {str(e)}")