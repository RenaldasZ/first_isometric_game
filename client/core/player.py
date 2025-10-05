# client/core/player.py
from dataclasses import dataclass
from typing import List
from client.core.animation import Animation
from client.core.directions import DIRECTIONS


@dataclass
class Player:
    position: List[int]
    animation: Animation
    direction: str = "down"

    def request_move(self, direction: str, network) -> bool:
        """
        Request a move from the server.
        Returns True if move was sent, False if blocked (cooldown).
        """
        if direction in DIRECTIONS:
            self.animation.update_direction(direction)
        else:
            print(f"[Player] invalid move direction: {direction}")

        try:
            network.send_move(direction)
        except Exception:
            pass

        return True
