import pygame
import sys

pygame.init()

# Screen settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Isometric Ground Effect with Player")

# Colors and tile settings
TILE_WIDTH, TILE_HEIGHT = 256, 128
BACKGROUND_COLOR = (0, 128, 128)
TILE_COLOR = (153, 101, 21)
PLAYER_TILE_COLOR = (255, 0, 0)
GRID_COLOR = (0, 0, 0)

player_pos = [5, 5]

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

# Main loop
clock = pygame.time.Clock()
grid_width, grid_height = 20, 20

try:
    while True:
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

        # Draw isometric grid with offsets
        draw_grid(screen, grid_width, grid_height, offset_x, offset_y)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Key handling for movement
        keys = pygame.key.get_pressed()

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