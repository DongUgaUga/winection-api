from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.models import WebSocketMessage
import json
from core.logging import logger

# WebSocket 연결을 관리할 방(room) 딕셔너리
rooms = {}

slts_router = APIRouter()

@slts_router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    try:
        await websocket.accept()
        logger.info(f"Client가 Room:[{room_id}]에 접속했습니다.")

        if room_id not in rooms:
            rooms[room_id] = []
        rooms[room_id].append(websocket)

        while True:
            try:
                # WebSocket: 데이터 수신
                data = await websocket.receive_text()
                try:
                    parsed_data = json.loads(data)  # JSON 파싱
                    message_type = parsed_data.get("type", {})
                    # hand_type = parsed_data.get("data", {}).get("hand_data", [])[0]["hand_type"]
                    message_data = parsed_data.get("data", {})
                    # hand_data = message_data['hand_data']

                    message = WebSocketMessage(type=message_type, data=message_data)

                except Exception as e:
                    logger.error(f"Room:[{room_id}] - 잘못된 WebSocket 메시지 수신: {e}")
                    continue  # 잘못된 데이터 무시하고 다음 메시지 처리

                
                # logger.info(f"수신 메시지: {parsed_data}, 손 타입: {message_type}, 손 좌표: {message_data['hand_data']}")
                # logger.info(f"Room:[{room_id}] - 수신 메시지: {message.json()}")
                # logger.info(f"{message.type}")
                # WebRTC 시그널링 데이터 처리
                if message.type in ["offer", "answer", "candidate"]:
                    # logger.info(f"Room:[{room_id}] - WebRTC 메시지 수신: {message.type}")
                    for ws in list(rooms.get(room_id, [])):
                        if ws != websocket:
                            try:
                                await ws.send_text(message.json())
                            except Exception as e:
                                logger.error(f"Room:[{room_id}] - WebRTC 시그널 전송 중 오류 발생: {e}")
                                rooms[room_id].remove(ws)

                # 손 좌표 데이터 처리
                elif message.type == "hand_data":
                    hand_data = message.data if isinstance(message.data, dict) else {}
                    for ws in list(rooms.get(room_id, [])):
                        try:
                            await ws.send_json({
                                "client_id": "peer" if ws != websocket else "self",
                                "hand_data": hand_data
                            })
                            
                            # logger.info(f"{hand_data}")
                        except Exception as e:
                            logger.error(f"Room:[{room_id}] - 손 좌표 데이터 전송 중 오류 발생: {e}")
                            rooms[room_id].remove(ws)

            except WebSocketDisconnect:
                logger.info(f"Client가 Room:[{room_id}]에서 나갔습니다.")
                if websocket in rooms.get(room_id, []):
                    rooms[room_id].remove(websocket)
                    if not rooms[room_id]:  # 방에 아무도 없으면 삭제
                        del rooms[room_id]
                break
            except Exception as e:
                logger.error(f"Room:[{room_id}] - 데이터 처리 중 오류 발생: {e}")
                continue  # 오류 발생 시 해당 클라이언트 무시

    except WebSocketDisconnect:
        logger.info(f"Client가 Room:[{room_id}]에서 나갔습니다.")
        if websocket in rooms.get(room_id, []):
            rooms[room_id].remove(websocket)
        if not rooms.get(room_id):
            del rooms[room_id]
    except Exception as e:
        logger.error(f"WebSocket 연결 처리 중 오류 발생: {e}")
        if room_id in rooms and websocket in rooms[room_id]:
            rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]