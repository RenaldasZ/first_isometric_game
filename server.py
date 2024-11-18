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

        # Send the client its unique ID
        await socket.send_text(json.dumps({"client_id": client_id}))

        await self.broadcast_message(json.dumps({"message": f"Player {client_id} connected"}))

    async def on_disconnect(self, socket: WebSocket) -> None:
        client_id = next((cid for cid, info in connected_clients.items() if info["socket"] == socket), None)
        if client_id:
            del connected_clients[client_id]
            await self.broadcast_message(json.dumps({"id": client_id, "disconnected": True}))

    async def on_receive(self, socket: WebSocket, data: str) -> None:
        client_id = next((cid for cid, info in connected_clients.items() if info["socket"] == socket), None)
        if client_id:
            parsed_data = json.loads(data)
            position_data = parsed_data.get("position")
            direction_data = parsed_data.get("direction")
            
            if position_data:
                connected_clients[client_id]["position"] = position_data
                connected_clients[client_id]["direction"] = direction_data
                await self.broadcast_message(json.dumps({
                    "id": client_id,
                    "position": position_data,
                    "direction": direction_data
                }))

    async def broadcast_message(self, message: str) -> None:
        for client in connected_clients.values():
            try:
                await client["socket"].send_text(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")

app = Litestar([Handler])
