from typing import Dict, List
import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Maps seller_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, seller_id: str):
        await websocket.accept()
        if seller_id not in self.active_connections:
            self.active_connections[seller_id] = []
        self.active_connections[seller_id].append(websocket)

    def disconnect(self, websocket: WebSocket, seller_id: str):
        if seller_id in self.active_connections:
            self.active_connections[seller_id].remove(websocket)
            if not self.active_connections[seller_id]:
                del self.active_connections[seller_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict, seller_id: str):
        if seller_id in self.active_connections:
            for connection in self.active_connections[seller_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception:
                    pass

    async def listen_to_redis(self):
        import redis.asyncio as aioredis
        from app.core.config import settings
        
        while True:
            try:
                redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                pubsub = redis_client.pubsub()
                await pubsub.psubscribe("channel:*")
                
                async for message in pubsub.listen():
                    if message["type"] == "pmessage":
                        # channel name is like "channel:seller_id"
                        channel = message["channel"]
                        seller_id = channel.split(":")[1]
                        data = message["data"]
                        try:
                            payload = json.loads(data)
                            await self.broadcast(payload, seller_id)
                        except Exception:
                            pass
            except Exception as e:
                # Reconnect on error
                await asyncio.sleep(5)

manager = ConnectionManager()



@router.websocket("/ws/{seller_id}")
async def websocket_endpoint(websocket: WebSocket, seller_id: str):
    """
    WebSocket endpoint for the UI to subscribe to real-time progress events.
    """
    await manager.connect(websocket, seller_id)
    try:
        while True:
            # We don't strictly need to receive data from the client,
            # but we need to keep the connection open and listen for disconnects
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, seller_id)
