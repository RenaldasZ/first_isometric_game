# server/game/logic.py
from server.state import server_state
from server.config import settings


class GameLogic:
    """Encapsulates game-specific rules and operations."""

    @staticmethod
    def move_player(client_id: str, direction: str) -> bool:
        """Attempt to move a player in the given direction.

        Returns:
            bool: True if movement succeeded, False if invalid or out of bounds.
        """
        player = server_state.get_client(client_id)
        if not player:
            return False

        pos = player["position"]
        dx, dy = 0, 0

        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        elif direction == "up_left":
            dx, dy = -1, -1
        elif direction == "up_right":
            dx, dy = 1, -1
        elif direction == "down_left":
            dx, dy = -1, 1
        elif direction == "down_right":
            dx, dy = 1, 1
        else:
            return False  # unknown direction

        new_x, new_y = pos[0] + dx, pos[1] + dy

        # Stay inside grid using settings
        if not (0 <= new_x < settings.GRID_WIDTH and 0 <= new_y < settings.GRID_HEIGHT):
            return False

        # Update state
        player["position"] = [new_x, new_y]
        player["direction"] = direction
        return True
