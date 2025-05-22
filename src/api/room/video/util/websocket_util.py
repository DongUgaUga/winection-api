from collections import defaultdict
from asyncio import Queue
from fastapi import WebSocket
from core.log.logging import logger

async def sender_loop(ws: WebSocket, room_id: str, queue: Queue):
    try:
        while True:
            message = await queue.get()
            if message is None:
                break
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.error(f"[{room_id}] 메시지 전송 실패 (큐): {e}")
                break
    finally:
        pass

def remove_client(ws, room_id, rooms, client_labels, user_nicknames, user_types, user_words, last_prediction_time, prev_predictions, send_queues):
    if ws in rooms.get(room_id, []):
        rooms[room_id].remove(ws)
    try:
        send_queues[ws].put_nowait(None)
    except:
        pass
    client_labels.pop(ws, None)
    user_nicknames.pop(ws, None)
    user_types.pop(ws, None)
    user_words.pop(ws, None)
    last_prediction_time.pop(ws, None)
    prev_predictions.pop(ws, None)
    send_queues.pop(ws, None)

async def notify_peer_leave(ws, room_id, rooms, send_queues, client_labels, remove_client_func):
    for peer in list(rooms.get(room_id, [])):
        if peer != ws:
            try:
                await send_queues[peer].put({"type": "leave", "client_id": "peer"})
            except Exception as e:
                logger.error(f"[{room_id}] leave 알림 전송 실패: {e}")
                remove_client_func(peer, room_id, rooms, client_labels, {}, {}, {}, {}, {}, send_queues)
