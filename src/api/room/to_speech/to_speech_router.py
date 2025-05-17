from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
import asyncio
from datetime import datetime, timedelta, timezone

from core.log.logging import logger
from src.api.room.to_speech.services.sign_to_text import ksl_to_korean
from src.api.room.to_speech.services.text_to_sentence import words_to_sentence, stop_words_to_sentence

import jwt
from jwt import PyJWTError
from core.db.database import SessionLocal
from core.auth.models import User
from core.auth.dependencies import SECRET_KEY, ALGORITHM

from collections import defaultdict
from asyncio import Queue

router = APIRouter()

MAX_ROOM_CAPACITY = 4

camera_refresh_tracker: dict[str, dict] = {}
client_labels: dict[WebSocket, str] = {}
user_nicknames: dict[WebSocket, str] = {}
user_types: dict[WebSocket, str] = {}
room_call_start_time: dict[str, str] = {}
prev_predictions: dict[WebSocket, str] = {}
user_words: dict[WebSocket, list] = {}
last_prediction_time: dict[WebSocket, datetime] = {}
send_queues: dict[WebSocket, Queue] = defaultdict(Queue)

async def sender_loop(ws: WebSocket, room_id: str):
    queue = send_queues[ws]
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
        send_queues.pop(ws, None)

async def handle_landmark(ws: WebSocket, room_id: str, d: dict):
    rooms = ws.app.state.rooms
    try:
        prediction = ksl_to_korean(d)
    except Exception as e:
        logger.exception(f"[{room_id}] 예측 중 예외 발생: {e}")
        prediction = ""

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
                remove_client(peer, room_id)

async def monitor_prediction_timeout(ws: WebSocket, room_id: str):
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
                for peer in ws.app.state.rooms.get(room_id, []):
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

def get_user_info_from_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise ValueError("유효하지 않은 토큰입니다 (sub 없음)")

        db = SessionLocal()
        user = db.query(User).filter(User.username == username).first()
        db.close()

        if user is None:
            raise ValueError("해당 유저를 찾을 수 없습니다")

        return {
            "nickname": user.nickname,
            "user_type": user.user_type
        } 
    except PyJWTError:
        raise ValueError("유효하지 않은 토큰입니다 (JWT 에러)")

def remove_client(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    if ws in rooms.get(room_id, []):
        rooms[room_id].remove(ws)
        
    try:
        send_queues[ws].put_nowait(None)
    except:
        pass
    
    client_labels.pop(ws, None)
    user_nicknames.pop(ws, None)
    user_words.pop(ws, None)
    last_prediction_time.pop(ws, None)
    prev_predictions.pop(ws, None)
    send_queues.pop(ws, None)

async def notify_peer_leave(ws: WebSocket, room_id: str):
    rooms = ws.app.state.rooms
    for peer in list(rooms.get(room_id, [])):
        if peer != ws:
            try:
                await send_queues[peer].put({"type": "leave", "client_id": "peer"})
            except Exception as e:
                logger.error(f"[{room_id}] leave 알림 전송 실패: {e}")
                remove_client(peer, room_id)


@router.websocket("/ws/slts/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str, token: str = Query(...)):
    try:
        user_info = get_user_info_from_token(token)
        nickname = user_info["nickname"]
        user_type = user_info["user_type"]
    except ValueError as e:
        await ws.close(code=1008, reason=str(e))
        logger.warning(f"[{room_id}] WebSocket 인증 실패: {e}")
        return

    rooms = ws.app.state.rooms
    pending = ws.app.state.pending_signals

    if room_id not in rooms:
        rooms[room_id] = []
        logger.info(f"[{room_id}] 새 방이 생성되었습니다.")

    if len(rooms[room_id]) >= MAX_ROOM_CAPACITY:
        await ws.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과로 접속 거부 (현재 인원: {len(rooms[room_id])})")
        return

    await ws.accept()
    send_queues[ws] = Queue()
    asyncio.create_task(sender_loop(ws, room_id))
    
    label = "self" if len(rooms[room_id]) == 0 else "peer"
    client_labels[ws] = label
    
    rooms[room_id].append(ws)
    
    user_nicknames[ws] = nickname
    user_types[ws] = user_type
    user_words[ws] = []
    last_prediction_time[ws] = datetime.utcnow()
    logger.info(f"👤 [{label}] Room:[{room_id}]에 접속했습니다. (현재 인원: {len(rooms[room_id])})")

    KST = timezone(timedelta(hours=9))
    room_call_start_time[room_id] = datetime.now(KST).isoformat(timespec="seconds")

    for target in rooms[room_id]:
        for peer in rooms[room_id]:
            await send_queues[target].put({
                "type": "startCall",
                "client_id": "peer" if target != peer else "self",
                "nickname": user_nicknames.get(peer, "알 수 없음"),
                "user_type": user_types.get(peer, "일반인"),
                "started_at": room_call_start_time[room_id]
            })

    asyncio.create_task(monitor_prediction_timeout(ws, room_id))

    try:
        while True:
            data = await ws.receive_text()
            parsed = json.loads(data)
            t = parsed.get("type")
            d = parsed.get("data")

            if t == "land_mark":
                asyncio.create_task(handle_landmark(ws, room_id, d))

            elif t in ["offer", "answer", "candidate"]:
                logger.info(f"Room:[{room_id}] - {client_labels[ws]} → WebRTC 메시지: {t}")
                payload = json.dumps({"type": t, "data": d})
                for peer in list(rooms[room_id]):
                    if peer != ws:
                        try:
                            await send_queues[peer].put({"type": t, "data": d})
                        except Exception as e:
                            logger.error(f"[{room_id}] WebRTC 전송 실패: {e}")
                            pending.setdefault(room_id, []).append((peer, payload))
                            remove_client(peer, room_id)

            elif t in ["camera_state", "mic_state"]:
                for peer in rooms[room_id]:
                    try:
                        await send_queues[peer].put({
                            "type": t,
                            "client_id": "peer" if peer != ws else "self",
                            "data": d
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 상태 전송 실패({t}): {e}")

            elif t == "startCall":
                room_call_start_time[room_id] = datetime.utcnow().isoformat()
                for peer in rooms[room_id]:
                    try:
                        await send_queues[peer].put({
                            "type": "startCall",
                            "client_id": "peer" if peer != ws else "self",
                            "nickname": user_nicknames.get(ws, "알 수 없음"),
                            "user_type": user_types.get(ws, "일반인"),
                            "started_at": room_call_start_time[room_id]
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] startCall 전송 실패: {e}")

            else:
                logger.warning(f"[{room_id}] 지원되지 않는 메시지 타입: {t}")

    except WebSocketDisconnect:
        logger.info(f"[{client_labels.get(ws)}] Room:[{room_id}]에서 나갔습니다.")
        await notify_peer_leave(ws, room_id)
        remove_client(ws, room_id)

    except Exception as e:
        logger.error(f"[{room_id}] websocket 처리 오류: {e}", exc_info=True)
        remove_client(ws, room_id)