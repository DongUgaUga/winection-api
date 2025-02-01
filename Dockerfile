FROM python:3.9-slim-buster

WORKDIR /src
COPY . .


# Build-time 환경변수 추가
ARG GOOGLE_API_KEY
ARG DEEPSEEK_API_KEY

# 환경변수 설정
ENV GOOGLE_CLOUD_API_KEY=$GOOGLE_API_KEY
ENV DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY

RUN apt update && apt install libpq-dev gcc -y && pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# docker buildx build --platform linux/amd64 -t woo204/winection-api:0.0.1 --push .
# docker pull woo204/winection-api:0.0.1
# docker run -d --name woo -p 8000:8000 woo204/winection-api:0.0.1