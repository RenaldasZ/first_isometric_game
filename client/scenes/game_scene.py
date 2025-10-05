# client/scenes/game_scene.py
import pygame
from client.core.state import GameState
from client.core.grid import cart_to_iso, iso_to_cart, draw_tile, draw_grid
from client.core.input import InputHandler
from client.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BACKGROUND_COLOR, TILE_COLOR, PLAYER_TILE_COLOR, OTHER_PLAYER_TILE_COLOR,
    GRID_WIDTH, GRID_HEIGHT, FPS, TILE_WIDTH, TILE_HEIGHT,
)
from client.ui.hud import draw_hud

class GameScene:
    def __init__(self, screen: pygame.Surface, state: GameState, network):
        self.screen = screen
        self.state = state
        self.network = network
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.input_handler = InputHandler(state, network)

    def process_messages(self) -> None:
        """Handle queued messages from the server."""
        while True:
            msg = self.state.pop_message()
            if msg is None:
                break
            msg_type = msg.get("type")
            if msg_type == "init":
                self.state.update_init(msg.get("client_id"), msg.get("players", {}))
            elif msg_type == "player_join":
                self.state.add_player(msg["id"], {"position": msg["position"], "direction": msg.get("direction", "down")})
            elif msg_type == "player_leave":
                self.state.remove_player(msg["id"])
            elif msg_type == "player_update":
                self.state.update_player(msg["id"], {"position": msg["position"], "direction": msg.get("direction", "down")})

    def handle_input(self, events) -> None:
        player = self.state.player
        if not player:
            return
        offset_x = (SCREEN_WIDTH // 2) - cart_to_iso(int(player.position[0]), int(player.position[1]))[0]
        offset_y = (SCREEN_HEIGHT // 2) - cart_to_iso(int(player.position[0]), int(player.position[1]))[1]

        self.input_handler.handle(events, offset_x, offset_y)

    def draw_world(self) -> None:
        player = self.state.player
        if not player:
            return

        offset_x = (SCREEN_WIDTH // 2) - cart_to_iso(int(player.position[0]), int(player.position[1]))[0]
        offset_y = (SCREEN_HEIGHT // 2) - cart_to_iso(int(player.position[0]), int(player.position[1]))[1]

        # draw tiles
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                iso_x, iso_y = cart_to_iso(col, row)
                iso_x += offset_x
                iso_y += offset_y
                draw_tile(self.screen, iso_x, iso_y, TILE_COLOR)

        # draw grid overlay
        draw_grid(self.screen, GRID_WIDTH, GRID_HEIGHT, offset_x, offset_y)

        # draw main player
        player_iso_x, player_iso_y = cart_to_iso(int(player.position[0]), int(player.position[1]))
        player_iso_x += offset_x
        player_iso_y += offset_y
        draw_tile(self.screen, player_iso_x, player_iso_y, PLAYER_TILE_COLOR)
        player.animation.draw_player(self.screen, player_iso_x, player_iso_y)

        # draw other players
        for pid, info in self.state.other_players.items():
            pos = info["position"]
            direction = info.get("direction", "down")
            iso_x, iso_y = cart_to_iso(pos[0], pos[1])
            iso_x += offset_x
            iso_y += offset_y
            draw_tile(self.screen, iso_x, iso_y, OTHER_PLAYER_TILE_COLOR)
            img = player.animation.get_image_by_direction(direction)
            w, h = img.get_size()
            self.screen.blit(img, (iso_x - w // 2, iso_y - h // 2))

        # debug: highlight tile under mouse and draw mouse pos
        mx, my = pygame.mouse.get_pos()
        iso_mx = mx - offset_x
        iso_my = my - offset_y
        gx, gy = iso_to_cart(iso_mx, iso_my)

        # tile iso top vertex
        iso_tx, iso_ty = cart_to_iso(gx, gy)
        iso_tx += offset_x
        iso_ty += offset_y

        # red outline of the tile we map to
        hw = int(TILE_WIDTH // 2)
        hh = int(TILE_HEIGHT // 2)
        points = [
            (int(iso_tx), int(iso_ty)),
            (int(iso_tx + hw), int(iso_ty + hh)),
            (int(iso_tx), int(iso_ty + TILE_HEIGHT)),
            (int(iso_tx - hw), int(iso_ty + hh)),
        ]
        pygame.draw.polygon(self.screen, (255, 0, 0), points, 2)
        pygame.draw.circle(self.screen, (255, 0, 0), (mx, my), 3)

    def run_once(self) -> None:
        """One tick: process events, messages, input, update, and draw."""
        events = pygame.event.get()

        # handle quit
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

        # process network + input
        self.process_messages()
        self.handle_input(events)

        # render
        self.screen.fill(BACKGROUND_COLOR)
        self.draw_world()
        draw_hud(self.screen, self.font, self.state)

        pygame.display.flip()
        self.clock.tick(FPS)
