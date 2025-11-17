"""Database manager for the Life Planner application."""

import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from .config import Config


logger = logging.getLogger(__name__)

# Create the base class for SQLAlchemy models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, config: Config):
        """Initialize database manager with configuration."""
        self.config = config
        self.engine = None
        self.SessionLocal = None

        logger.info("Database Manager initialized")

    def initialize(self):
        """Initialize database engine and create tables."""
        # Ensure database directory exists
        db_path = Path(self.config.database_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        if self.config.database_url.startswith("sqlite"):
            # For SQLite, use the path from config
            database_url = f"sqlite:///{self.config.database_path}"
        else:
            database_url = self.config.database_url

        self.engine = create_engine(database_url, echo=self.config.debug)

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        # Import all models to ensure they're registered
        # TODO: Import actual models when implemented
        # from ..modules.food_tracker.models import FoodEntry
        # from ..modules.water_tracker.models import WaterEntry
        # from ..modules.gym_tracker.models import WorkoutEntry

        # Create all tables
        Base.metadata.create_all(bind=self.engine)

        logger.info("Database initialized at %s", database_url)

    def get_session(self) -> Session:
        """Get a database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()

    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")

    def get_status(self) -> dict:
        """Get database status."""
        status = {
            "initialized": self.engine is not None,
            "database_url": self.config.database_url if self.engine else None,
        }

        if self.engine:
            try:
                with self.engine.connect() as conn:
                    conn.execute("SELECT 1")
                status["connected"] = True
            except Exception as e:
                status["connected"] = False
                status["error"] = str(e)

        return status
