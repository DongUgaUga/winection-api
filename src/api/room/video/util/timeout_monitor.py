import asyncio
from datetime import datetime, timedelta
from core.log.logging import logger
from src.api.room.video.util.room_manager import room_manager

TIMEOUT_SECONDS = 3

async def monitor_prediction_timeout(ws, room_id):
    try:
        while True:
            await asyncio.sleep(1)
            last_time = room_manager.last_prediction_time.get(ws)
            if last_time is None:
                continue

            now = datetime.utcnow()
            if (now - last_time) > timedelta(seconds=TIMEOUT_SECONDS):
                words = room_manager.user_words.get(ws, [])
                if words:
                    logger.info(f"[{room_id}] 🛑 예측 중단 감지 – 누적 단어: {words}")
                    await room_manager.send_queues[ws].put({
                        "type": "sentence",
                        "client_id": "self",
                        "words": words
                    })
                    room_manager.user_words[ws] = []
    except Exception as e:
        logger.error(f"[{room_id}] monitor_prediction_timeout 오류: {e}", exc_info=True)