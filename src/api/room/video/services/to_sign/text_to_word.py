import openai
from core.config.env_config import OPENAI_API_KEY
from core.log.logging import logger

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def text_to_word(sentence: str, word_list: list[str]) -> list[str]:
    system_prompt = (
        f"너는 수어 통역사야.\n"
        f"사용자가 문장을 입력하면, 반드시 아래 '단어 목록'에 존재하는 단어로만 이루어진 수어 어순의 단어 나열로 변환해야 해.\n"
        f"단어 목록에 없는 단어는 **절대 출력하지 말고**, 의미가 통하는 가장 가까운 단어로 대체하거나 생략해.\n"
        f"부정의 경우 '아니다'를 넣어줘\n"
        f"문장이랑 비슷하게 가려고 단어 목록에 없는거 꺼내면 내가 처리하기 힘들어져.\n\n"
        f"형식은 다음과 같아:\n"
        f"단어1 단어2 단어3 (공백 구분)\n\n"
        f"단어 목록에 없는 단어는 출력 금지!\n"
        f"단어 목록: [{', '.join(word_list)}]\n\n"
        f"예시:\n"
        f"- 입력1: 낯선사람이 우리집에 들어왔어요. 경찰을 불러주세요.\n"
        f"- 출력1: 낮선사람 우리집 경찰 보내주세요(경찰)\n"
        f"- 입력2: 배가 아파요. 병원 가고 싶어요.\n"
        f"- 출력2: 복통 병원\n"
        f"- 입력3: 손목이 멀쩡해요\n"
        f"- 출력3: 손목 아니다 부러지다 (멀쩡해요 같은 경우에는 의미가 통하는 가장 가까운 단어인 '아니다', '부러지다'로 넣었어)\n"
    )
    user_prompt = (
        f"\n"
        f"문장: {sentence}\n\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o", # "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            max_tokens=100,
        )
        result_text = response.choices[0].message.content.strip()
        return result_text.split()

    except Exception as e:
        logger.error(f"[GPT] 단어 추출 실패: {e}")
        return []