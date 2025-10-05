# client/core/grid.py
import pygame
from client.config import TILE_WIDTH, TILE_HEIGHT

TILE_WIDTH_HALF = TILE_WIDTH // 2
TILE_HEIGHT_HALF = TILE_HEIGHT // 2

def cart_to_iso(cart_x: int, cart_y: int) -> tuple[int, int]:
    iso_x = (cart_x - cart_y) * TILE_WIDTH_HALF
    iso_y = (cart_x + cart_y) * TILE_HEIGHT_HALF
    return iso_x, iso_y

def iso_to_cart(iso_x: int, iso_y: int) -> tuple[int, int]:
    cart_x = (iso_x / TILE_WIDTH_HALF + iso_y / TILE_HEIGHT_HALF) / 2
    cart_y = (iso_y / TILE_HEIGHT_HALF - iso_x / TILE_WIDTH_HALF) / 2
    return int(cart_x), int(cart_y)

def draw_tile(screen: pygame.Surface, x: int, y: int, color: tuple[int, int, int]):
    points = [
        (x, y),
        (x + TILE_WIDTH_HALF, y + TILE_HEIGHT_HALF),
        (x, y + TILE_HEIGHT),
        (x - TILE_WIDTH_HALF, y + TILE_HEIGHT_HALF),
    ]
    pygame.draw.polygon(screen, color, points)

def draw_grid(screen: pygame.Surface, grid_width: int, grid_height: int, offset_x: int, offset_y: int):
    for row in range(grid_height):
        for col in range(grid_width):
            iso_x, iso_y = cart_to_iso(col, row)
            iso_x += offset_x
            iso_y += offset_y
            # draw tile outline
            pygame.draw.line(screen, (0,0,0), (iso_x, iso_y), (iso_x + TILE_WIDTH_HALF, iso_y + TILE_HEIGHT_HALF))
            pygame.draw.line(screen, (0,0,0), (iso_x + TILE_WIDTH_HALF, iso_y + TILE_HEIGHT_HALF), (iso_x, iso_y + TILE_HEIGHT))
            pygame.draw.line(screen, (0,0,0), (iso_x, iso_y + TILE_HEIGHT), (iso_x - TILE_WIDTH_HALF, iso_y + TILE_HEIGHT_HALF))
            pygame.draw.line(screen, (0,0,0), (iso_x - TILE_WIDTH_HALF, iso_y + TILE_HEIGHT_HALF), (iso_x, iso_y))
