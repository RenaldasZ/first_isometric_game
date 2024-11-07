from litestar import Litestar, WebSocket
from litestar.handlers import WebsocketListener
import uuid

connected_clients = {}

class Handler(WebsocketListener):
    """Handler for WebSocket connections, managing connected clients and broadcasting messages."""
    
    path = "/"

    async def on_accept(self, socket: WebSocket) -> None:
        """
        Handles new client connections.

        Args:
            socket (WebSocket): The WebSocket connection for the client.

        Generates a unique client ID, stores the client in the connected clients list,
        and broadcasts a connection message to all connected clients.
        """
        client_id = str(uuid.uuid4())
        connected_clients[client_id] = {"socket": socket}
        print(f"Connection accepted, Client ID: {client_id}")
        await self.broadcast_message(f"Player {client_id} connected")

    async def on_disconnect(self, socket: WebSocket) -> None:
        """
        Handles client disconnections.

        Args:
            socket (WebSocket): The WebSocket connection for the client.

        Finds the client ID associated with the socket, removes the client from the 
        connected clients list, and broadcasts a disconnection message.
        """
        client_id = next((cid for cid, info in connected_clients.items() if info["socket"] == socket), None)
        if client_id:
            del connected_clients[client_id]
            print(f"Connection closed {client_id}")
            await self.broadcast_message(f"Player {client_id} disconnected")

    async def on_receive(self, socket: WebSocket, data: str) -> None:
        """
        Handles incoming data from clients.

        Args:
            socket (WebSocket): The WebSocket connection for the client.
            data (str): The data received from the client.

        Echoes the received data back to the client.
        """
        await socket.send_text(data)
    
    async def broadcast_message(self, message: str) -> None:
        """
        Broadcasts a message to all connected clients.

        Args:
            message (str): The message to broadcast.

        Sends the specified message to each connected client. If an error occurs
        while sending a message, logs the error without interrupting the loop.
        """
        for client in connected_clients.values():
            try:
                await client["socket"].send_text(message)
            except Exception as e:
                print(f"Error sending message to client: {e}")

# Instantiate the Litestar app with the Handler
app = Litestar([Handler])
