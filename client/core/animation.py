# client/core/animation.py
from pathlib import Path
import pygame
from client.config import ANIM_IMG_SIZE

class Animation:
    def __init__(self, assets_dir: Path):
        """Load directional images from assets_dir (Path to assets/media)."""
        self.assets_dir = assets_dir
        # The path calculation assumes package root is first_isometric_game/.
        # assets should be at first_isometric_game/assets/media/.
        try:
            self.down_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_down.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.up_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_up.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.left_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_left.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.right_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_right.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.down_right_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_down_right.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.up_right_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_up_right.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.up_left_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_up_left.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
            self.down_left_img = pygame.transform.scale(
                pygame.image.load(str(self.assets_dir / "t_down_left.png")).convert_alpha(),
                ANIM_IMG_SIZE,
            )
        except Exception as e:
            # If images fail to load, create placeholders
            print(f"[Animation] failed to load images: {e}. Using placeholders.")
            self.down_img = pygame.Surface(ANIM_IMG_SIZE, pygame.SRCALPHA)
            self.down_img.fill((200, 200, 200))
            self.up_img = self.down_img.copy()
            self.left_img = self.down_img.copy()
            self.right_img = self.down_img.copy()
            self.down_right_img = self.down_img.copy()
            self.up_right_img = self.down_img.copy()
            self.up_left_img = self.down_img.copy()
            self.down_left_img = self.down_img.copy()

        self.current_img = self.down_img

    def update_direction(self, direction: str) -> None:
        if direction == "up":
            self.current_img = self.up_img
        elif direction == "down":
            self.current_img = self.down_img
        elif direction == "left":
            self.current_img = self.left_img
        elif direction == "right":
            self.current_img = self.right_img
        elif direction == "down_right":
            self.current_img = self.down_right_img
        elif direction == "up_right":
            self.current_img = self.up_right_img
        elif direction == "up_left":
            self.current_img = self.up_left_img
        elif direction == "down_left":
            self.current_img = self.down_left_img

    def get_image_by_direction(self, direction: str):
        return {
            "up": self.up_img,
            "down": self.down_img,
            "left": self.left_img,
            "right": self.right_img,
            "down_right": self.down_right_img,
            "up_right": self.up_right_img,
            "up_left": self.up_left_img,
            "down_left": self.down_left_img,
        }.get(direction, self.down_img)

    def draw_player(self, screen, iso_x, iso_y):
        """Draw the currently selected image centered on the tile."""
        # Offsets assume image center is tile center; tweak if needed
        w, h = self.current_img.get_size()
        screen.blit(self.current_img, (iso_x - w // 2, iso_y - h // 2))
