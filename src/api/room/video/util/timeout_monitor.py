import asyncio
from datetime import datetime
from core.log.logging import logger
from src.api.room.video.services.to_speech.text_to_sentence import words_to_sentence, stop_words_to_sentence

async def monitor_prediction_timeout(ws, room_id, user_words, last_prediction_time, send_queues, rooms):
    while True:
        await asyncio.sleep(1)
        if ws not in last_prediction_time:
            continue

        elapsed = datetime.utcnow() - last_prediction_time[ws]
        if elapsed.total_seconds() >= 3:
            words = user_words.get(ws, [])
            if words:
                sentence = stop_words_to_sentence(words)
                logger.info(f"[{room_id}] 📝 문장 생성됨: {sentence}")
                for peer in rooms.get(room_id, []):
                    try:
                        await send_queues[peer].put({
                            "type": "sentence",
                            "client_id": "peer" if peer != ws else "self",
                            "result": sentence
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 문장 전송 실패: {e}")
                user_words[ws] = []
                last_prediction_time[ws] = datetime.utcnow()