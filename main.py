import pygame
import sys
import websocket
import threading
import queue
import json
import time
import logging

logging.basicConfig(level=logging.DEBUG)

pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric Ground Effect with Player")

# Colors and tile settings
TILE_WIDTH, TILE_HEIGHT = 256, 128
BACKGROUND_COLOR = (0, 128, 128)
TILE_COLOR = (153, 101, 21)
PLAYER_TILE_COLOR = (255, 0, 0)
OTHER_PLAYER_TILE_COLOR = (0, 0, 255)
GRID_COLOR = (0, 0, 0)

# Function to convert cartesian coordinates to isometric
def cart_to_iso(cart_x, cart_y):
    iso_x = (cart_x - cart_y) * (TILE_WIDTH // 2)
    iso_y = (cart_x + cart_y) * (TILE_HEIGHT // 2)
    return iso_x, iso_y

# Function to draw an isometric tile
def draw_tile(screen, x, y, color):
    points = [
        (x, y),
        (x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2),
        (x, y + TILE_HEIGHT),
        (x - TILE_WIDTH // 2, y + TILE_HEIGHT // 2)
    ]
    pygame.draw.polygon(screen, color, points)

# Function to draw the grid lines
def draw_grid(screen, grid_width, grid_height, offset_x, offset_y):
    for row in range(grid_height):
        for col in range(grid_width):
            iso_x, iso_y = cart_to_iso(col, row)
            iso_x += offset_x
            iso_y += offset_y
            pygame.draw.line(screen, GRID_COLOR, (iso_x, iso_y), (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2))
            pygame.draw.line(screen, GRID_COLOR, (iso_x + TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2), (iso_x, iso_y + TILE_HEIGHT))
            pygame.draw.line(screen, GRID_COLOR, (iso_x, iso_y + TILE_HEIGHT), (iso_x - TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2))
            pygame.draw.line(screen, GRID_COLOR, (iso_x - TILE_WIDTH // 2, iso_y + TILE_HEIGHT // 2), (iso_x, iso_y))

# WebSocket event handlers with improvements
class Game:
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.player_pos = [5, 5]
        self.other_players = {}
        self.connection_status = "Disconnected"
        self.message_queue = queue.Queue()
        self.ws_thread = threading.Thread(target=self.run_websocket, daemon=True)
        self.ws_thread.start()

    def on_open(self, ws):
        self.is_connected = True
        self.message_queue.put("Connected")

    def on_close(self, ws, close_status_code, close_msg):
        self.is_connected = False
        self.message_queue.put("Disconnected")
        self.reconnect()

    def on_message(self, ws, message):
        self.message_queue.put(f"Message: {message}")
        try:
            if message.strip():  
                data = json.loads(message)
                if "id" in data and "position" in data:
                    self.other_players[data["id"]] = data["position"]
            else:
                logging.warning("Received an empty message from the server.")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON message: {e}")

    def reconnect(self):
        while not self.is_connected:
            try:
                logging.debug("Trying to reconnect...")
                self.ws = websocket.WebSocketApp(
                    "ws://127.0.0.1:8000/",
                    on_open=self.on_open,
                    on_close=self.on_close,
                    on_message=self.on_message
                )
                self.ws.run_forever()
            except Exception as e:
                logging.error(f"Reconnection failed: {e}")
                time.sleep(2)

    def run_websocket(self):
        self.reconnect()

    def send_player_position(self):
        if self.is_connected:
            try:
                data = json.dumps({"position": self.player_pos})
                self.ws.send(data)
            except websocket.WebSocketConnectionClosedException:
                print("Failed to send position: WebSocket connection closed")
        else:
            print("Cannot send position: Not connected to server")

# Main loop
game = Game()
clock = pygame.time.Clock()
grid_width, grid_height = 20, 20
font = pygame.font.Font(None, 36)

try:
    while True:
        # # Process WebSocket messages
        while not game.message_queue.empty():
            msg = game.message_queue.get()
            if "Connected" in msg:
                game.connection_status = "Connected"
            elif "Disconnected" in msg:
                game.connection_status = "Disconnected"
            else:
                print(msg)

        screen.fill(BACKGROUND_COLOR)

        offset_x = (SCREEN_WIDTH // 2) - cart_to_iso(game.player_pos[0], game.player_pos[1])[0]
        offset_y = (SCREEN_HEIGHT // 2) - cart_to_iso(game.player_pos[0], game.player_pos[1])[1]

        # Draw isometric grid with offsets
        for row in range(grid_height):
            for col in range(grid_width):
                iso_x, iso_y = cart_to_iso(col, row)
                if (game.player_pos[0], game.player_pos[1]) == (col, row):
                    draw_tile(screen, iso_x + offset_x, iso_y + offset_y, PLAYER_TILE_COLOR)
                elif any((p[0], p[1]) == (col, row) for p in game.other_players.values()):
                    draw_tile(screen, iso_x + offset_x, iso_y + offset_y, OTHER_PLAYER_TILE_COLOR)
                else:
                    draw_tile(screen, iso_x + offset_x, iso_y + offset_y, TILE_COLOR)

        draw_grid(screen, grid_width, grid_height, offset_x, offset_y)

        # Connection status display
        status_text = font.render(f"Status: {game.connection_status}", True, (255, 255, 255))
        screen.blit(status_text, (10, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movement controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and game.player_pos[1] > 0:
            game.player_pos[1] -= 1
        if keys[pygame.K_DOWN] and game.player_pos[1] < grid_height - 1:
            game.player_pos[1] += 1
        if keys[pygame.K_LEFT] and game.player_pos[0] > 0:
            game.player_pos[0] -= 1
        if keys[pygame.K_RIGHT] and game.player_pos[0] < grid_width - 1:
            game.player_pos[0] += 1

        game.send_player_position()
        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("Game closed")
