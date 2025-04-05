# Python 3.9 + Debian Bullseye 환경 사용
FROM --platform=linux/amd64 python:3.9-slim-bullseye

WORKDIR /src

# 필수 패키지 설치
RUN apt update && apt install -y \
    libpq-dev gcc \
    && apt clean && rm -rf /var/lib/apt/lists/*

# requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# wait-for-it.sh 복사 및 권한 설정
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# 전체 프로젝트 복사
COPY . .

EXPOSE 8000

# 🔥 핵심! MySQL(db:3306) 연결될 때까지 기다린 뒤 FastAPI 실행
CMD ["/wait-for-it.sh", "db:3306", "--", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src"]