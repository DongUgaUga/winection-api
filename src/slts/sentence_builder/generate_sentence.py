from openai import OpenAI
import os
from dotenv import load_dotenv
import logging

# 환경변수 로드
load_dotenv()

# API 키 설정
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("환경변수 'DEEPSEEK_API_KEY'가 설정되지 않았습니다.")


# OpenAI 클라이언트 초기화
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# DeepSeek API 호출 함수
def generate_sentence(words: list) -> str:
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