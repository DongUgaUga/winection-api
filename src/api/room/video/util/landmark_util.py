from core.log.logging import logger
from src.api.room.video.util.predictor import SignPredictorFSM
from src.api.room.video.util.room_manager import room_manager

predictor = SignPredictorFSM()

async def handle_landmark(
    ws, room_id, data,
    rooms, send_queues
):
    try:
        landmarks = data.get("land_mark", [])
        sentence = predictor.predict(landmarks)

        if sentence:
            for peer in rooms[room_id]:
                if room_manager.user_types.get(peer) == "청인":
                    await send_queues[peer].put({
                        "type": "text",
                        "client_id": "peer" if peer != ws else "self",
                        "result": sentence
                    })

    except Exception as e:
        logger.error(f"[{room_id}] handle_landmark 처리 실패: {e}", exc_info=True)
