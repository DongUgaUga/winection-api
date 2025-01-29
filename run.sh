#!/usr/bin/env bash

# 패키지 설치 (이미 설치된 경우 스킵됨)
pip install --no-cache-dir -q -r requirements.txt

# FastAPI 서버 실행 (백그라운드)
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload &

# FastAPI PID 저장
UVICORN_PID=$!

# 프론트 테스트 용
# Python HTTP 서버 실행 (백그라운드)
python3 -m http.server 8080 --bind 0.0.0.0 &

# HTTP 서버 PID 저장
HTTP_PID=$!

# 스크립트를 종료하면 백그라운드 프로세스도 종료
trap "kill $UVICORN_PID $HTTP_PID" EXIT

# 대기
wait