from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections[user_id].append(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if websocket in self.connections[user_id]:
            self.connections[user_id].remove(websocket)

    async def broadcast(self, user_id: str, payload: dict) -> None:
        for websocket in list(self.connections[user_id]):
            await websocket.send_json(payload)


realtime_manager = ConnectionManager()

