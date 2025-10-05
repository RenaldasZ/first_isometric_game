import pygame
from client.core.state import GameState

def draw_hud(screen: pygame.Surface, font: pygame.font.Font, state: GameState) -> None:
    status_text = font.render(f"Status: {state.connection_status}", True, (255, 255, 255))
    screen.blit(status_text, (10, 10))

    player_count = len(state.other_players) + (1 if state.player else 0)
    player_count_text = font.render(f"Players Online: {player_count}", True, (255, 255, 255))
    screen.blit(player_count_text, (10, 50))
