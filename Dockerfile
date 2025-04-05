# Python 3.9 + Debian Bullseye 환경 사용
FROM --platform=linux/amd64 python:3.9-slim-bullseye

# 작업 디렉토리 설정
WORKDIR /src

# 필수 패키지 설치
RUN apt update && apt install -y \
    libpq-dev gcc \
    && apt clean && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# wait-for-it.sh 복사 및 실행 권한 부여
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# 전체 프로젝트 복사
COPY . .

# 포트 노출
EXPOSE 8000