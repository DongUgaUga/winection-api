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
                logger.error(f"[{room_id}] 메시지 전송 실패: {e}")
                break
    except Exception as e:
        logger.error(f"[{room_id}] sender_loop 오류: {e}", exc_info=True)

async def notify_peer_leave(ws, room_id, rooms, send_queues, client_labels, remove_client_func):
    for peer in list(rooms.get(room_id, [])):
        if peer != ws:
            try:
                await send_queues[peer].put({"type": "leave", "client_id": "peer"})
            except Exception as e:
                logger.error(f"[{room_id}] leave 알림 실패: {e}")
                remove_client_func(peer)