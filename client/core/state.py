# client/core/state.py
import queue
from typing import Dict, Optional
from client.core.player import Player

class GameState:
    """Local game state container."""

    def __init__(self):
        self.client_id: Optional[str] = None
        self.player: Optional[Player] = None
        # other_players maps id -> {"position": [x,y], "direction": str}
        self.other_players: Dict[str, dict] = {}
        self.message_queue: "queue.Queue[dict]" = queue.Queue()
        self.connection_status: str = "Disconnected"

    # helpers to mutate state (thread-safe queue used for messages)
    def push_message(self, msg: dict) -> None:
        self.message_queue.put(msg)

    def pop_message(self) -> Optional[dict]:
        try:
            return self.message_queue.get_nowait()
        except queue.Empty:
            return None

    def update_init(self, client_id: str, players: dict) -> None:
        self.client_id = client_id
        self.other_players = players.copy()

    def add_player(self, client_id: str, info: dict) -> None:
        self.other_players[client_id] = info.copy()

    def remove_player(self, client_id: str) -> None:
        self.other_players.pop(client_id, None)

    def update_player(self, client_id: str, info: dict) -> None:
        if client_id == self.client_id and self.player:
            # update local player's authoritative position
            self.player.position = info["position"]
            self.player.direction = info.get("direction", self.player.direction)
            self.player.animation.update_direction(self.player.direction)
        else:
            self.other_players[client_id] = info.copy()
