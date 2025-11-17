"""Base service class for all tracker modules."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class BaseTrackerService(ABC):
    """Abstract base service for all tracker modules."""

    def __init__(self, db_session: Session):
        """Initialize the service with a database session."""
        self.db_session = db_session
        self.service_name = self.__class__.__name__

    def initialize(self):
        """Initialize the service."""
        logger.info("%s initialized", self.service_name)

    def shutdown(self):
        """Shutdown the service."""
        logger.info("%s shutdown", self.service_name)

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get service status. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_status")

    @abstractmethod
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily summary. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_daily_summary")

    @abstractmethod
    def get_weekly_summary(
        self, start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get weekly summary. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement get_weekly_summary")

    def _handle_error(self, operation: str, error: Exception):
        """Common error handling for all services."""
        logger.error("Error in %s during %s: %s", self.service_name, operation, error)
        try:
            if hasattr(self.db_session, "rollback"):
                self.db_session.rollback()
        except Exception:
            pass  # Ignore rollback errors
        raise error

    def _get_current_date(self) -> datetime:
        """Get current date for consistent date handling."""
        return datetime.now()

    def _format_date(self, date: datetime) -> str:
        """Format date consistently across services."""
        if isinstance(date, datetime):
            return date.date().isoformat()
        return date.isoformat()
