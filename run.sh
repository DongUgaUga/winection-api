#!/usr/bin/env bash

# src 디렉터리를 PYTHONPATH에 추가
export PYTHONPATH=$(pwd)/src

# 패키지 설치 (이미 설치된 경우 스킵됨)
pip install --no-cache-dir -q -r requirements.txt

# FastAPI 서버 실행
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload