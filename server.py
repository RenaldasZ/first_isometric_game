from litestar import Litestar, WebSocket
from litestar.handlers import WebsocketListener
import uuid
import json

connected_clients = {}

class Handler(WebsocketListener):
    path = "/"

    async def on_accept(self, socket: WebSocket) -> None:
        client_id = str(uuid.uuid4())
        connected_clients[client_id] = {"socket": socket}
        await self.broadcast_message(json.dumps({"message": f"Player {client_id} connected"}))

    async def on_disconnect(self, socket: WebSocket) -> None:
        client_id = next((cid for cid, info in connected_clients.items() if info["socket"] == socket), None)
        if client_id:
            del connected_clients[client_id]
            await self.broadcast_message(json.dumps({"message": f"Player {client_id} disconnected"}))

    async def on_receive(self, socket: WebSocket, data: str) -> None:
        client_id = next((cid for cid, info in connected_clients.items() if info["socket"] == socket), None)
        if client_id:
            position_data = json.loads(data).get("position")
            if position_data:
                connected_clients[client_id]["position"] = position_data
                await self.broadcast_message(json.dumps({"id": client_id, "position": position_data}))

    async def broadcast_message(self, message: str) -> None:
        for client in connected_clients.values():
            try:
                await client["socket"].send_text(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")

app = Litestar([Handler])
