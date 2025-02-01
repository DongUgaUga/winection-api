import os
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

PROJECT_ID = 'winection-project'

GOOGLE_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", os.environ.get("GOOGLE_CLOUD_API_KEY"))
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", os.environ.get("DEEPSEEK_API_KEY"))

if not GOOGLE_API_KEY:
    raise ValueError("환경변수 'GOOGLE_CLOUD_API_KEY'가 설정되지 않았습니다.")


if not DEEPSEEK_API_KEY:
    raise ValueError("환경변수 'DEEPSEEK_API_KEY'가 설정되지 않았습니다.")

