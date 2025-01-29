import os
from dotenv import load_dotenv

# 프로젝트 ID
PROJECT_ID = "winection-project"

# 서비스 계정 JSON 파일 경로 (Google STT & TTS 인증용)
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not GOOGLE_APPLICATION_CREDENTIALS:
    raise ValueError("환경변수 'GOOGLE_APPLICATION_CREDENTIALS'가 설정되지 않았습니다.")

# DeepSeek API 키
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("환경변수 'DEEPSEEK_API_KEY'가 설정되지 않았습니다.")``