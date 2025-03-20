import os
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("환경변수 'GOOGLE_CLOUD_API_KEY'가 설정되지 않았습니다.")

PROJECT_ID = 'winection-project'

# OpenAI API 키 (환경 변수에서 로드)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("환경변수 'OPENAI_API_KEY'가 설정되지 않았습니다.")