import logging
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "winection-api.log")

# 로그 설정
logging.basicConfig(
    level=logging.INFO,  # 기본 로그 레벨 (INFO, DEBUG, ERROR 조절)
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)
