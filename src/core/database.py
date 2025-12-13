"""Enhanced Database manager with all models imported."""

import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
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

        # Import all models to ensure they're registered with Base
        try:
            from ..modules.auth.models import User
            from ..modules.food_tracker.models import FoodEntry
            from ..modules.water_tracker.models import WaterEntry
            from ..modules.gym_tracker.models import WorkoutEntry

            logger.info("All models imported successfully")
        except ImportError as e:
            logger.warning(f"Some models could not be imported: {e}")

        # Check if we need to migrate/rebuild the database
        self._migrate_database()

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

    def _migrate_database(self):
        """Migrate database schema to match models or recreate if needed."""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()

            # Get all table names from models
            model_tables = Base.metadata.tables.keys()

            # Check if schema matches for each table
            schema_mismatch = False

            for table_name in model_tables:
                if table_name not in existing_tables:
                    logger.info(f"Table {table_name} doesn't exist, will create")
                    continue

                # Get model columns
                model_table = Base.metadata.tables[table_name]
                model_columns = {col.name: col for col in model_table.columns}

                # Get existing columns
                existing_columns = {
                    col["name"]: col for col in inspector.get_columns(table_name)
                }

                # Check for missing columns in database
                missing_columns = set(model_columns.keys()) - set(
                    existing_columns.keys()
                )

                if missing_columns:
                    logger.warning(
                        f"Table {table_name} is missing columns: {missing_columns}"
                    )
                    schema_mismatch = True

                    # For SQLite, try to add missing columns
                    if self.config.database_url.startswith("sqlite"):
                        for col_name in missing_columns:
                            col = model_columns[col_name]
                            self._add_column_sqlite(table_name, col)

            # Create any missing tables
            Base.metadata.create_all(bind=self.engine)

            if schema_mismatch:
                logger.info("Database schema has been migrated to match models")
            else:
                logger.info("Database schema matches models")

        except Exception as e:
            logger.error(f"Error during database migration: {e}")
            logger.warning("Attempting to recreate all tables")
            # If migration fails, try to recreate all tables
            Base.metadata.create_all(bind=self.engine)

    def _add_column_sqlite(self, table_name: str, column):
        """Add a column to an SQLite table."""
        try:
            # Build ALTER TABLE statement
            col_type = column.type.compile(self.engine.dialect)
            nullable = "NULL" if column.nullable else "NOT NULL"

            # Handle default values
            default_clause = ""
            if column.default is not None:
                if hasattr(column.default, "arg"):
                    if callable(column.default.arg):
                        # For datetime.utcnow and similar, use NULL as default
                        default_clause = "DEFAULT NULL"
                    else:
                        default_clause = f"DEFAULT {column.default.arg}"

            # For nullable columns, we can add them directly
            if column.nullable:
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type} {default_clause}"
            else:
                # For NOT NULL columns, add with default first
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type} DEFAULT '' {nullable}"

            with self.engine.begin() as conn:
                conn.execute(text(alter_sql))

            logger.info(f"Added column {column.name} to table {table_name}")

        except Exception as e:
            logger.error(f"Failed to add column {column.name} to {table_name}: {e}")
            raise
