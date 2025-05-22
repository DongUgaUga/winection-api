from datetime import datetime
from core.log.logging import logger
from src.api.room.video.services.to_speech.sign_to_text import ksl_to_korean

async def handle_landmark(ws, room_id, d, rooms, send_queues, prev_predictions, user_words, last_prediction_time):
    try:
        prediction = ksl_to_korean(d)
    except Exception as e:
        logger.exception(f"[{room_id}] 예측 중 예외 발생: {e}")
        return

    if not prediction:
        return

    prev = prev_predictions.get(ws, "")
    if prediction != prev:
        prev_predictions[ws] = prediction
        user_words[ws].append(prediction)
        last_prediction_time[ws] = datetime.utcnow()

        for peer in list(rooms[room_id]):
            try:
                await send_queues[peer].put({
                    "type": "text",
                    "client_id": "peer" if peer != ws else "self",
                    "result": ", ".join(user_words[ws])
                })
            except Exception as e:
                logger.error(f"[{room_id}] 예측 전송 실패: {e}")