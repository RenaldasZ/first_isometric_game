# server/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration with environment overrides."""

    GRID_WIDTH: int = 40
    GRID_HEIGHT: int = 40
    MAX_PLAYERS: int = 100
    DEBUG: bool = True

    class Config:
        env_prefix = "GAME_"  # environment variables must start with GAME_


settings = Settings()
