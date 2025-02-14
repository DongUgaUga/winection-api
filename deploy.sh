#!/usr/bin/env bash
# 학교 내부 인터넷 망에서만 실행 가능!!

set -e

echo "🚀 Docker 이미지 빌드 중..."
docker buildx build --platform linux/amd64 -t woo204/winection-api:latest --push . || { echo "❌ Docker 이미지 빌드 실패!"; exit 1; }

echo "📪 Docker Hub에 이미지 푸시 완료!"

REMOTE_USER="woo"
REMOTE_HOST="218.150.182.161"
REMOTE_PORT="20831"

REMOTE_COMMANDS="
echo '🛠️ 기존 컨테이너 정리 중...'
(docker stop api || true) > /dev/null
(docker rm api || true) > /dev/null
(docker rmi woo204/winection-api:latest || true) > /dev/null

echo '🐳 Docker 데몬 상태 확인...'
if ! systemctl is-active --quiet docker; then
    echo '❌ Docker 데몬이 실행되지 않음! 서버에서 Docker를 실행해주세요.'
    exit 1
fi

echo '📦 최신 이미지 다운로드 중...'
docker pull woo204/winection-api:latest || { echo '❌ Docker 이미지 다운로드 실패!'; exit 1; }

echo '🐳 컨테이너 실행 중...'
docker run -d --name api -p 8000:8000 woo204/winection-api:latest || { echo '❌ 컨테이너 실행 실패!'; exit 1; }

echo '🎉 배포 완료!'
"

# SSH를 통해 원격 서버에서 실행
echo "🔗 원격 서버(${REMOTE_HOST})에 접속하여 배포 진행 중..."
ssh -p $REMOTE_PORT $REMOTE_USER@$REMOTE_HOST "$REMOTE_COMMANDS" || { echo "❌ SSH 연결 실패!"; exit 1; }

echo "✅ 모든 배포 과정 완료!"
