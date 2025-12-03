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
    secret_key: str

    # Module settings
    food_tracker_enabled: bool
    water_tracker_enabled: bool
    gym_tracker_enabled: bool


def get_config() -> Config:
    """Get application configuration from environment variables and defaults."""

    # Get base path - goes up from src/core/ to project root
    base_path = Path(__file__).parent.parent.parent

    return Config(
        # Database
        database_url=os.getenv("DATABASE_URL", "sqlite:///data/life_planner.db"),
        database_path=os.getenv(
            "DATABASE_PATH",
            str(base_path / "data" / "life_planner.db"),  # Creates in data/ directory
        ),
        # Frontend
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        debug=os.getenv("DEBUG", "False").lower() == "true",
        # Application
        app_name=os.getenv("APP_NAME", "Life Planner"),
        version=os.getenv("VERSION", "1.0.0"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
        # Modules
        food_tracker_enabled=os.getenv("FOOD_TRACKER_ENABLED", "True").lower()
        == "true",
        water_tracker_enabled=os.getenv("WATER_TRACKER_ENABLED", "True").lower()
        == "true",
        gym_tracker_enabled=os.getenv("GYM_TRACKER_ENABLED", "True").lower() == "true",
    )
