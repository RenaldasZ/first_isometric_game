# server/state.py
from typing import Optional, TypedDict
from litestar import WebSocket


class ClientInfo(TypedDict):
    socket: WebSocket
    position: list[int]
    direction: str


class ServerState:
    """Global in-memory server state.

    This manages all connected clients and their associated data.
    For scalability, this can later be replaced with Redis or a database.
    """

    def __init__(self) -> None:
        self.connected_clients: dict[str, ClientInfo] = {}

    # --- Client lifecycle ---

    def register_client(
        self,
        client_id: str,
        socket: WebSocket,
        pos: tuple[int, int] = (5, 5),
        direction: str = "down",
    ) -> None:
        """Add a new client to the state."""
        self.connected_clients[client_id] = {
            "socket": socket,
            "position": list(pos),
            "direction": direction,
        }

    def remove_client(self, client_id: str) -> Optional[ClientInfo]:
        """Remove client by ID and return its info if it existed."""
        return self.connected_clients.pop(client_id, None)

    def get_client(self, client_id: str) -> Optional[ClientInfo]:
        """Lookup client info by ID."""
        return self.connected_clients.get(client_id)

    def get_client_by_socket(self, socket: WebSocket) -> Optional[str]:
        """Find the client_id for a given WebSocket, or None if not found."""
        return next(
            (cid for cid, info in self.connected_clients.items() if info["socket"] == socket),
            None,
        )

    # --- Utility ---

    def all_clients(self) -> dict[str, ClientInfo]:
        """Return all currently connected clients."""
        return self.connected_clients

    def count(self) -> int:
        """Return how many clients are connected."""
        return len(self.connected_clients)


# Create a single shared instance
server_state = ServerState()
