from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.app.services.realtime import realtime_manager

websocket_router = APIRouter()


@websocket_router.websocket("/ws/{user_id}")
async def training_updates(websocket: WebSocket, user_id: str) -> None:
    await realtime_manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        realtime_manager.disconnect(user_id, websocket)

