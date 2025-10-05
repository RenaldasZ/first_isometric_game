# client/main.py
"""
Client entrypoint.
Run from project root:
    python -m client.main
"""
import logging
import pygame
import sys
from pathlib import Path

from client.config import SCREEN_WIDTH, SCREEN_HEIGHT
from client.core.animation import Animation
from client.core.player import Player
from client.core.state import GameState
from client.core.network import Network
from client.scenes.game_scene import GameScene

logger = logging.getLogger("client")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Isometric Multiplayer (Client)")

    # Assets directory: project_root/assets/media
    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "media"

    # Setup state & network
    state = GameState()
    network = Network("ws://127.0.0.1:8000/", state)
    network_thread = network.start()  # background thread for WebSocket

    # Create local player with animation
    animation = Animation(assets_dir)
    player = Player([5, 5], animation)
    state.player = player

    scene = GameScene(screen, state, network)

    try:
        while True:
            # run one frame of the scene (handles events, updates, drawing)
            scene.run_once()

            # --- Watchdog check for dead network thread ---
            if not network_thread.is_alive():
                logger.error("Network thread died unexpectedly! Restarting...")
                network_thread = network.start()

    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down client...")

    finally:
        network.stop()
        if network_thread:
            network_thread.join(timeout=1)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()
