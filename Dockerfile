# 작업 디렉토리 설정
FROM WORKDIR /src

# 필수 패키지 설치 (gcc, libpq-dev 필요 시 유지)
RUN apt update && apt install -y \
    libpq-dev gcc \
    && apt clean && rm -rf /var/lib/apt/lists/*

# requirements.txt 복사 후 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 프로젝트 코드 복사
COPY . .

# ✅ SSL 인증서 복사 (컨테이너 내부로 인증서 파일 이동)
COPY /etc/letsencrypt/live/winection.kro.kr/fullchain.pem /etc/ssl/certs/fullchain.pem
COPY /etc/letsencrypt/live/winection.kro.kr/privkey.pem /etc/ssl/private/privkey.pem

# 포트 노출
EXPOSE 8000

# FastAPI 실행 (SSL 적용)
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "src", \
     "--ssl-keyfile", "/etc/ssl/private/privkey.pem", "--ssl-certfile", "/etc/ssl/certs/fullchain.pem"]
