import os
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# Google Cloud 서비스 계정 JSON 파일 경로
GOOGLE_CLOUD_CREDENTIALS_PATH = "secret/google-cloud-api-key.json"

if not os.path.exists(GOOGLE_CLOUD_CREDENTIALS_PATH):
    raise ValueError(f"서비스 계정 파일이 존재하지 않습니다: {GOOGLE_CLOUD_CREDENTIALS_PATH}")

# 환경 변수에 서비스 계정 JSON 적용
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_CREDENTIALS_PATH

# Google Cloud 프로젝트 ID (JSON에서 로드)
with open(GOOGLE_CLOUD_CREDENTIALS_PATH, "r") as f:
    google_credentials = json.load(f)
    PROJECT_ID = google_credentials.get("project_id")

if not PROJECT_ID:
    raise ValueError("Google Cloud 프로젝트 ID가 설정되지 않았습니다.")

# DeepSeek API 키 (환경 변수에서 로드)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("환경변수 'DEEPSEEK_API_KEY'가 설정되지 않았습니다.")