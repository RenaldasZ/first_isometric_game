# client/core/input.py
import pygame
from heapq import heappush, heappop
from client.core.grid import iso_to_cart
from client.config import GRID_WIDTH, GRID_HEIGHT
from client.core.directions import DIRECTION_VECTORS


class InputHandler:
    """
    Handles player input and A* pathfinding for click-to-move and hold-to-move controls.
    Now also prepared for pixel-based movement.
    """

    def __init__(self, state, network):
        self.state = state
        self.network = network
        self.path_queue: list[str] = []
        self.mouse_held = False
        self.last_mouse_tile = None

        # For pixel movement preparation
        self.current_input_direction = None  # e.g., "up_right"
        self.is_pathfinding_active = False   # differentiate between auto and manual move

    # -------------------------------------------------------------
    # Public entry point
    # -------------------------------------------------------------
    def handle(self, events, offset_x: int = 0, offset_y: int = 0) -> None:
        player = self.state.player
        if not player:
            return

        # Handle both keyboard and mouse input
        self._handle_keyboard(events)
        self._handle_mouse(events, player, offset_x, offset_y)

        # If pathfinding is active (mouse), follow queued path
        if self.is_pathfinding_active:
            self._process_path(player)

        # If keyboard input is active, move continuously (coming later)
        elif self.current_input_direction:
            player.request_move(self.current_input_direction, self.network)

    # -------------------------------------------------------------
    # Keyboard input (for pixel movement)
    # -------------------------------------------------------------
    def _handle_keyboard(self, events) -> None:
        keys = pygame.key.get_pressed()

        # Determine direction combination
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Match direction to our centralized direction names
        self.current_input_direction = None
        for name, (vx, vy) in DIRECTION_VECTORS.items():
            if (vx, vy) == (dx, dy):
                self.current_input_direction = name
                break

        # Disable pathfinding when keyboard used
        if self.current_input_direction:
            self.is_pathfinding_active = False

    # -------------------------------------------------------------
    # Mouse input (click-to-move)
    # -------------------------------------------------------------
    def _handle_mouse(self, events, player, offset_x: int, offset_y: int) -> None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.mouse_held = True
                self.is_pathfinding_active = True  # activate auto move mode

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.mouse_held = False
                self.last_mouse_tile = None

        if self.mouse_held:
            mx, my = pygame.mouse.get_pos()
            iso_x = mx - offset_x
            iso_y = my - offset_y
            grid_x, grid_y = iso_to_cart(iso_x, iso_y)

            if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
                return

            goal = (int(grid_x), int(grid_y))
            start = tuple(map(int, player.position))

            if goal != self.last_mouse_tile:
                self.last_mouse_tile = goal
                self.path_queue = self.find_path(start, goal)
                if self.path_queue:
                    print(f"[Path] {start} -> {goal}: {self.path_queue}")

    # -------------------------------------------------------------
    # Path execution (used by mouse click-to-move)
    # -------------------------------------------------------------
    def _process_path(self, player) -> None:
        if not self.path_queue:
            self.is_pathfinding_active = False
            return

        direction = self.path_queue[0]
        if player.request_move(direction, self.network):
            self.path_queue.pop(0)

    # -------------------------------------------------------------
    # A* pathfinding (8-way)
    # -------------------------------------------------------------
    def find_path(self, start, goal):
        dirs = {
            (dx, dy): (name, (1.414 if dx != 0 and dy != 0 else 1))
            for name, (dx, dy) in DIRECTION_VECTORS.items()
        }

        def heuristic(a, b):
            dx = abs(a[0] - b[0])
            dy = abs(a[1] - b[1])
            return dx + dy - min(dx, dy) + 1.414 * min(dx, dy)

        open_set = []
        heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        visited = set()

        while open_set:
            _, current = heappop(open_set)
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                break

            for (dx, dy), (direction, cost) in dirs.items():
                neighbor = (current[0] + dx, current[1] + dy)
                if not (0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT):
                    continue

                tentative_g = g_score[current] + cost
                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = (current, direction)
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f, neighbor))

        # reconstruct path
        path_dirs = []
        node = goal
        while node in came_from:
            prev, direction = came_from[node]
            path_dirs.append(direction)
            node = prev
        path_dirs.reverse()
        return path_dirs
