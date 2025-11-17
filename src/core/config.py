"""Configuration module for the Life Planner application."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Application configuration."""

    # Database configuration
    database_url: str
    database_path: str

    # Frontend configuration
    host: str
    port: int
    debug: bool

    # Application settings
    app_name: str
    version: str
    log_level: str

    # Module settings
    food_tracker_enabled: bool
    water_tracker_enabled: bool
    gym_tracker_enabled: bool


def get_config() -> Config:
    """Get application configuration from environment variables and defaults."""

    # Get base path
    base_path = Path(__file__).parent.parent.parent

    return Config(
        # Database
        database_url=os.getenv("DATABASE_URL", "sqlite:///life_planner.db"),
        database_path=os.getenv(
            "DATABASE_PATH", str(base_path / "data" / "life_planner.db")
        ),
        # Frontend
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8443")),
        debug=os.getenv("DEBUG", "False").lower() == "true",
        # Application
        app_name=os.getenv("APP_NAME", "Life Planner"),
        version=os.getenv("VERSION", "1.0.0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        # Modules
        food_tracker_enabled=os.getenv("FOOD_TRACKER_ENABLED", "True").lower()
        == "true",
        water_tracker_enabled=os.getenv("WATER_TRACKER_ENABLED", "True").lower()
        == "true",
        gym_tracker_enabled=os.getenv("GYM_TRACKER_ENABLED", "True").lower() == "true",
    )
