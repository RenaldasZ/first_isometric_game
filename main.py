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

# Animation class to handle player movement animations
class Animation:
    def __init__(self):
        # Load player images for each direction
        self.down_img = pygame.transform.scale(pygame.image.load("media/t_down.png"), (200, 200))
        self.up_img = pygame.transform.scale(pygame.image.load("media/t_up.png"), (200, 200))
        self.left_img = pygame.transform.scale(pygame.image.load("media/t_left.png"), (200, 200))
        self.right_img = pygame.transform.scale(pygame.image.load("media/t_right.png"), (200, 200))
        self.current_img = self.down_img  # Default player image

    def update_direction(self, direction):
        """Update player image based on the direction."""
        if direction == "up":
            self.current_img = self.up_img
        elif direction == "down":
            self.current_img = self.down_img
        elif direction == "left":
            self.current_img = self.left_img
        elif direction == "right":
            self.current_img = self.right_img

    def get_image_by_direction(self, direction):
        """Return the corresponding image for a given direction string."""
        if direction == "up":
            return self.up_img
        elif direction == "down":
            return self.down_img
        elif direction == "left":
            return self.left_img
        elif direction == "right":
            return self.right_img
        return self.down_img  # Default image if direction is unknown

    def draw_player(self, screen, iso_x, iso_y):
        screen.blit(self.current_img, (iso_x - 100, iso_y - 100))

# WebSocket event handlers with improvements
class Game:
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.player_pos = [5, 5]
        self.other_players = {}
        self.client_id = None
        self.connection_status = "Disconnected"
        self.message_queue = queue.Queue()
        self.ws_thread = threading.Thread(target=self.run_websocket, daemon=True)
        self.ws_thread.start()
        self.animation = Animation()

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
                
                # Store the client_id if it's in the message
                if "client_id" in data:
                    self.client_id = data["client_id"]
                
                if data.get("disconnected"):
                    player_id = data["id"]
                    if player_id in self.other_players:
                        del self.other_players[player_id]
                elif "id" in data and "position" in data:
                    # Avoid storing main player in other_players
                    if data["id"] != self.client_id:
                        self.other_players[data["id"]] = {
                            "position": data["position"],
                            "direction": data.get("direction")
                        }
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
                # Map current image to a direction string
                direction = (
                    "up" if self.animation.current_img == self.animation.up_img else
                    "down" if self.animation.current_img == self.animation.down_img else
                    "left" if self.animation.current_img == self.animation.left_img else
                    "right"
                )

                # Send the position and direction
                data = json.dumps({"position": self.player_pos, "direction": direction})
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
        # Process WebSocket messages
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
                iso_x += offset_x
                iso_y += offset_y
                draw_tile(screen, iso_x, iso_y, TILE_COLOR)

        # Draw the main player separately
        player_iso_x, player_iso_y = cart_to_iso(game.player_pos[0], game.player_pos[1])
        player_iso_x += offset_x
        player_iso_y += offset_y
        draw_tile(screen, player_iso_x, player_iso_y, PLAYER_TILE_COLOR)
        game.animation.draw_player(screen, player_iso_x, player_iso_y)

        # Draw other players
        for player_id, player_info in game.other_players.items():
            other_player_pos = player_info["position"]
            other_player_direction = player_info.get("direction", "down")

            other_player_iso_x, other_player_iso_y = cart_to_iso(other_player_pos[0], other_player_pos[1])
            other_player_iso_x += offset_x
            other_player_iso_y += offset_y
            draw_tile(screen, other_player_iso_x, other_player_iso_y, OTHER_PLAYER_TILE_COLOR)

            # Get the correct image based on the direction
            other_player_img = game.animation.get_image_by_direction(other_player_direction)
            screen.blit(other_player_img, (other_player_iso_x - 100, other_player_iso_y - 100))

        draw_grid(screen, grid_width, grid_height, offset_x, offset_y)

        # Connection status display
        status_text = font.render(f"Status: {game.connection_status}", True, (255, 255, 255))
        screen.blit(status_text, (10, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("Game closing..")
                game.ws.close()
                pygame.quit()
                sys.exit()

        # Movement controls
        keys = pygame.key.get_pressed()

        movement_keys = {
            pygame.K_UP: ("up", 0, -1),
            pygame.K_DOWN: ("down", 0, 1),
            pygame.K_LEFT: ("left", -1, 0),
            pygame.K_RIGHT: ("right", 1, 0)
        }

        for key, (direction, dx, dy) in movement_keys.items():
            if keys[key]:
                new_x = game.player_pos[0] + dx
                new_y = game.player_pos[1] + dy

                # Add boundary checks
                if 0 <= new_x < grid_width and 0 <= new_y < grid_height:
                    game.player_pos[0] = new_x
                    game.player_pos[1] = new_y
                    game.animation.update_direction(direction)
                break

        game.send_player_position()
        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("Game closing..")
    game.ws.close()
    pygame.quit()
    sys.exit()