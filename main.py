import pygame
import sys
import websocket
import threading
import queue

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
GRID_COLOR = (0, 0, 0)

player_pos = [5, 5]
connection_status = "Disconnected"  # Initial status

# Queue for thread-safe communication between WebSocket and main Pygame loop
message_queue = queue.Queue()

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
def on_open(ws):
    message_queue.put("Connected")

def on_close(ws, close_status_code, close_msg):
    message_queue.put("Disconnected")
    # Attempt reconnection if disconnected
    reconnect()

def on_message(ws, message):
    message_queue.put(f"Message: {message}")

def reconnect():
    try:
        ws = websocket.WebSocketApp("ws://127.0.0.1:8000/", on_open=on_open, on_close=on_close, on_message=on_message)
        ws.run_forever()
    except Exception as e:
        print(f"Reconnection failed: {e}")
        message_queue.put("Disconnected")

def run_websocket():
    reconnect()  # Start connection with auto-reconnect enabled

# Start WebSocket thread
ws_thread = threading.Thread(target=run_websocket)
ws_thread.daemon = True
ws_thread.start()

# Main loop
clock = pygame.time.Clock()
grid_width, grid_height = 20, 20
font = pygame.font.Font(None, 36)

try:
    while True:
        # Handle queued WebSocket messages for thread safety
        while not message_queue.empty():
            msg = message_queue.get()
            if "Connected" in msg:
                connection_status = "Connected"
            elif "Disconnected" in msg:
                connection_status = "Disconnected"
            else:
                print(msg)  # Handle game-related messages here

        screen.fill(BACKGROUND_COLOR)

        offset_x = (SCREEN_WIDTH // 2) - cart_to_iso(player_pos[0], player_pos[1])[0]
        offset_y = (SCREEN_HEIGHT // 2) - cart_to_iso(player_pos[0], player_pos[1])[1]

        # Draw isometric grid with offsets
        for row in range(grid_height):
            for col in range(grid_width):
                iso_x, iso_y = cart_to_iso(col, row)
                if (player_pos[0], player_pos[1]) == (col, row):
                    draw_tile(screen, iso_x + offset_x, iso_y + offset_y, PLAYER_TILE_COLOR)
                else:
                    draw_tile(screen, iso_x + offset_x, iso_y + offset_y, TILE_COLOR)

        draw_grid(screen, grid_width, grid_height, offset_x, offset_y)


        # Display connection status
        status_text = font.render(f"Status: {connection_status}", True, (255, 255, 255))
        screen.blit(status_text, (10, 10))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Key handling for movement
        keys = pygame.key.get_pressed()
        direction = None
        moved = False
        if keys[pygame.K_UP] and player_pos[1] > 0:
            player_pos[1] -= 1
            direction = "up"
            moved = True
        if keys[pygame.K_DOWN] and player_pos[1] < grid_height - 1:
            player_pos[1] += 1
            direction = "down"
            moved = True
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= 1
            direction = "left"
            moved = True
        if keys[pygame.K_RIGHT] and player_pos[0] < grid_width - 1:
            player_pos[0] += 1
            direction = "right"
            moved = True

        if moved:
            print(direction)

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    print("Game closed")
