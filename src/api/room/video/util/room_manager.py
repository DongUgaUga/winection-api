from collections import defaultdict
from asyncio import Queue
from datetime import datetime
from typing import Dict, List
from fastapi import WebSocket

from src.api.room.video.services.to_speech.sign_to_text import SignPredictorState

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}
        self.send_queues: Dict[WebSocket, Queue] = defaultdict(Queue)
        self.user_words: Dict[WebSocket, List[str]] = {}
        self.client_labels: Dict[WebSocket, str] = {}
        self.user_nicknames: Dict[WebSocket, str] = {}
        self.user_types: Dict[WebSocket, str] = {}
        self.last_prediction_time: Dict[WebSocket, datetime] = {}
        self.prev_predictions: Dict[WebSocket, str] = {}

        self.sign_states: Dict[WebSocket, SignPredictorState] = {}

    def join(self, room_id: str, ws: WebSocket, nickname: str, user_type: str) -> str:
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(ws)

        self.user_words[ws] = []
        self.client_labels[ws] = "self" if len(self.rooms[room_id]) == 1 else "peer"
        self.user_nicknames[ws] = nickname
        self.user_types[ws] = user_type
        self.last_prediction_time[ws] = datetime.utcnow()
        self.prev_predictions[ws] = ""

        self.sign_states[ws] = SignPredictorState()

        return self.client_labels[ws]

    def disconnect(self, room_id: str, ws: WebSocket):
        if ws in self.rooms.get(room_id, []):
            self.rooms[room_id].remove(ws)

        try:
            self.send_queues[ws].put_nowait(None)
        except:
            pass

        for store in [
            self.send_queues, self.user_words, self.client_labels,
            self.user_nicknames, self.user_types,
            self.last_prediction_time, self.prev_predictions,
            self.sign_states
        ]:
            store.pop(ws, None)

    def get_peers(self, room_id: str) -> List[WebSocket]:
        return self.rooms.get(room_id, [])

    def is_full(self, room_id: str, max_capacity: int) -> bool:
        return len(self.rooms.get(room_id, [])) >= max_capacity

    def get_label(self, ws: WebSocket) -> str:
        return self.client_labels.get(ws, "unknown")

    def get_queue(self, ws: WebSocket) -> Queue:
        return self.send_queues[ws]

room_manager = RoomManager()
