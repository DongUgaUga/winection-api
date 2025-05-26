from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import json
import asyncio
from datetime import datetime, timedelta, timezone
from core.log.logging import logger

from src.api.room.video.util.room_manager import room_manager
from src.api.room.video.util.websocket_util import sender_loop, notify_peer_leave

from core.auth.dependencies import get_user_info_from_token
from core.auth.dependencies import get_db_context

from src.api.room.video.services.to_speech.sign_to_text import sign_to_text
from src.api.room.video.services.to_speech.text_to_sentence import text_to_sentence
from src.api.room.video.services.to_speech.sentence_to_speech import sentence_to_speech, get_voice_name

from src.api.room.video.services.to_sign.text_to_word import text_to_word
from src.api.room.video.services.to_sign.word_to_index import word_to_index, get_all_sign_words

router = APIRouter()

MAX_ROOM_CAPACITY = 4
room_call_start_time: dict[str, str] = {}

@router.websocket("/ws/video/{room_id}")
async def websocket_endpoint(ws: WebSocket, room_id: str, token: str = Query(...)):
    try:
        with get_db_context() as db:
            user = get_user_info_from_token(token, db)
            nickname = user.nickname
            user_type = user.user_type
    except ValueError as e:
        await ws.close(code=1008, reason=str(e))
        logger.warning(f"[{room_id}] WebSocket 인증 실패: {e}")
        return

    if room_manager.is_full(room_id, MAX_ROOM_CAPACITY):
        await ws.close(code=1008, reason="Room full")
        logger.info(f"[{room_id}] 방 인원 초과")
        return

    await ws.accept()
    label = room_manager.join(room_id, ws, nickname, user_type)
    asyncio.create_task(sender_loop(ws, room_id, room_manager.get_queue(ws)))

    logger.info(f"👤 [{label}] Room:[{room_id}] 역할: {user_type}, 등록됨")

    KST = timezone(timedelta(hours=9))
    room_call_start_time[room_id] = datetime.now(KST).isoformat(timespec="seconds")

    for peer in room_manager.get_peers(room_id):
        await room_manager.get_queue(peer).put({
            "type": "startCall",
            "client_id": "peer" if peer != ws else "self",
            "nickname": room_manager.user_nicknames.get(peer, "알 수 없음"),
            "user_type": room_manager.user_types.get(peer, "청인"),
            "started_at": room_call_start_time[room_id]
        })

    if user_type == "농인":
        logger.info(f"[{room_id}] 농인 좌표: ")

    try:
        while True:
            data = await ws.receive_text()
            parsed = json.loads(data)
            t = parsed.get("type")
            d = parsed.get("data")

            if t == "land_mark" and room_manager.user_types[ws] == "농인":
                try:
                    sequence = {"pose": d.get("land_mark", [])}
                    words = sign_to_text(sequence)

                    if words:
                        sentence = text_to_sentence(words)
                        logger.info(f"[{room_id}] 예측된 문장: {sentence}")

                        voice_label = parsed.get("voice", "성인 남자")
                        voice_name = get_voice_name(voice_label)
                        audio_base64 = sentence_to_speech(voice_name, sentence)

                        for peer in room_manager.get_peers(room_id):
                            if room_manager.user_types.get(peer) in ["청인", "응급기관"]:
                                await room_manager.get_queue(peer).put({
                                    "type": "sentence",
                                    "client_id": "peer" if peer != ws else "self",
                                    "sentence": sentence,
                                    "audio_base64": audio_base64
                                })
                except Exception as e: 
                    logger.error(f"[{room_id}] 수어 예측 실패: {e}", exc_info=True)


            elif t == "text" and room_manager.user_types[ws] in ["청인", "응급기관"]:
                input_text = str(d.get("text", ""))
                avatar = parsed.get("avatar")
                logger.info(f"[{room_id}] STT 텍스트 수신: {input_text}")

                motions = []
                results_for_log = []

                try:
                    with get_db_context() as db:
                        word_list = get_all_sign_words(db)
                        words = text_to_word(input_text, word_list)

                        for word in words:
                            idx = word_to_index(word, db)
                            if idx is not None:
                                motions.append({"word": word, "index": idx})
                                results_for_log.append(f"({word}, {idx})")
                            else:
                                logger.warning(f"[{room_id}] ⚠️ DB에 존재하지 않는 단어: '{word}'")
                except Exception as e:
                    logger.error(f"[{room_id}] text_to_word 또는 DB 처리 실패: {e}")
                    words = []

                if results_for_log:
                    logger.info(f"[{room_id}] 결과: {', '.join(results_for_log)}")
                else:
                    logger.warning(f"[{room_id}] 변환된 단어 중 유효한 인덱스 없음")

                for peer in room_manager.get_peers(room_id):
                    try:
                        await room_manager.get_queue(peer).put({
                            "type": "motions",
                            "client_id": "peer" if peer != ws else "self",
                            "avatar": avatar,
                            "data": motions
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 인덱스 전송 실패: {e}")

            elif t in ["offer", "answer", "candidate"]:
                payload = {"type": t, "data": d}
                for peer in room_manager.get_peers(room_id):
                    if peer != ws:
                        try:
                            await room_manager.get_queue(peer).put(payload)
                        except Exception as e:
                            logger.error(f"[{room_id}] WebRTC 전송 오류: {e}")

            elif t in ["camera_state", "mic_state"]:
                for peer in room_manager.get_peers(room_id):
                    try:
                        await room_manager.get_queue(peer).put({
                            "type": t,
                            "client_id": "peer" if peer != ws else "self",
                            "data": d
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] 상태 전송 실패({t}): {e}")

            elif t == "startCall":
                room_call_start_time[room_id] = datetime.utcnow().isoformat()
                for peer in room_manager.get_peers(room_id):
                    try:
                        await room_manager.get_queue(peer).put({
                            "type": "startCall",
                            "client_id": "peer" if peer != ws else "self",
                            "nickname": room_manager.user_nicknames.get(ws, "알 수 없음"),
                            "user_type": room_manager.user_types.get(ws, "청인"),
                            "started_at": room_call_start_time[room_id]
                        })
                    except Exception as e:
                        logger.error(f"[{room_id}] startCall 전송 실패: {e}")

            else:
                logger.warning(f"[{room_id}] 지원되지 않는 메시지 타입: {t}")

    except WebSocketDisconnect:
        logger.info(f"[{room_id}] 로그아웃: {room_manager.get_label(ws)}")
        await notify_peer_leave(
            ws, room_id,
            room_manager.rooms,
            room_manager.send_queues,
            room_manager.client_labels,
            room_manager.disconnect
        )
        room_manager.disconnect(room_id, ws)

    except Exception as e:
        logger.error(f"[{room_id}] WebSocket 처리 오류: {e}", exc_info=True)
        room_manager.disconnect(room_id, ws)