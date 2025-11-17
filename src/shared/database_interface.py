"""Database interface for reusable database operations."""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Type, TypeVar
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

logger = logging.getLogger(__name__)

# Generic type for model classes
ModelType = TypeVar("ModelType")


class BaseRepository(ABC):
    """Abstract base repository for database operations."""

    def __init__(self, db_session: Session, model_class: Type[ModelType]):
        """Initialize repository with database session and model class."""
        self.db_session = db_session
        self.model_class = model_class

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        try:
            instance = self.model_class(**kwargs)
            self.db_session.add(instance)
            self.db_session.commit()
            self.db_session.refresh(instance)

            logger.info(
                "Created %s record with id: %s",
                self.model_class.__name__,
                getattr(instance, "id", "N/A"),
            )
            return instance

        except Exception as e:
            self.db_session.rollback()
            logger.error("Failed to create %s record: %s", self.model_class.__name__, e)
            raise

    def get_by_id(self, record_id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        try:
            return (
                self.db_session.query(self.model_class)
                .filter(self.model_class.id == record_id)
                .first()
            )
        except Exception as e:
            logger.error(
                "Failed to get %s record by id %s: %s",
                self.model_class.__name__,
                record_id,
                e,
            )
            raise

    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[ModelType]:
        """Get all records with optional pagination."""
        try:
            query = self.db_session.query(self.model_class)

            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            return query.all()

        except Exception as e:
            logger.error(
                "Failed to get all %s records: %s", self.model_class.__name__, e
            )
            raise

    def update(self, record_id: int, **kwargs) -> Optional[ModelType]:
        """Update a record by ID."""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            # Update timestamp if available
            if hasattr(instance, "updated_at"):
                instance.updated_at = datetime.utcnow()

            self.db_session.commit()
            self.db_session.refresh(instance)

            logger.info(
                "Updated %s record with id: %s", self.model_class.__name__, record_id
            )
            return instance

        except Exception as e:
            self.db_session.rollback()
            logger.error(
                "Failed to update %s record %s: %s",
                self.model_class.__name__,
                record_id,
                e,
            )
            raise

    def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        try:
            instance = self.get_by_id(record_id)
            if not instance:
                return False

            self.db_session.delete(instance)
            self.db_session.commit()

            logger.info(
                "Deleted %s record with id: %s", self.model_class.__name__, record_id
            )
            return True

        except Exception as e:
            self.db_session.rollback()
            logger.error(
                "Failed to delete %s record %s: %s",
                self.model_class.__name__,
                record_id,
                e,
            )
            raise

    def count(self) -> int:
        """Count total records."""
        try:
            return self.db_session.query(self.model_class).count()
        except Exception as e:
            logger.error("Failed to count %s records: %s", self.model_class.__name__, e)
            raise

    def filter_by_date_range(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        date_field: str = "created_at",
    ) -> List[ModelType]:
        """Filter records by date range."""
        try:
            query = self.db_session.query(self.model_class)

            if hasattr(self.model_class, date_field):
                date_column = getattr(self.model_class, date_field)

                if start_date:
                    query = query.filter(date_column >= start_date)
                if end_date:
                    query = query.filter(date_column <= end_date)

            return query.order_by(getattr(self.model_class, date_field).desc()).all()

        except Exception as e:
            logger.error(
                "Failed to filter %s records by date: %s", self.model_class.__name__, e
            )
            raise

    def get_recent(self, limit: int = 10) -> List[ModelType]:
        """Get recent records ordered by creation date."""
        try:
            if hasattr(self.model_class, "created_at"):
                return (
                    self.db_session.query(self.model_class)
                    .order_by(self.model_class.created_at.desc())
                    .limit(limit)
                    .all()
                )
            else:
                return self.db_session.query(self.model_class).limit(limit).all()

        except Exception as e:
            logger.error(
                "Failed to get recent %s records: %s", self.model_class.__name__, e
            )
            raise


class DatabaseInterface:
    """High-level database interface for common operations."""

    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db_session = db_session
        self._repositories = {}

    def get_repository(self, model_class: Type[ModelType]) -> BaseRepository:
        """Get or create a repository for the given model class."""
        model_name = model_class.__name__

        if model_name not in self._repositories:
            self._repositories[model_name] = BaseRepository(
                self.db_session, model_class
            )

        return self._repositories[model_name]

    def execute_raw_query(
        self, query: str, params: Optional[Dict] = None
    ) -> List[Dict]:
        """Execute raw SQL query and return results as dictionaries."""
        try:
            result = self.db_session.execute(query, params or {})
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Failed to execute raw query: %s", e)
            raise

    def bulk_insert(
        self, model_class: Type[ModelType], data: List[Dict[str, Any]]
    ) -> List[ModelType]:
        """Bulk insert records for better performance."""
        try:
            instances = [model_class(**item) for item in data]
            self.db_session.bulk_save_objects(instances, return_defaults=True)
            self.db_session.commit()

            logger.info(
                "Bulk inserted %d %s records", len(instances), model_class.__name__
            )
            return instances

        except Exception as e:
            self.db_session.rollback()
            logger.error(
                "Failed to bulk insert %s records: %s", model_class.__name__, e
            )
            raise

    def get_session(self) -> Session:
        """Get the database session."""
        return self.db_session
