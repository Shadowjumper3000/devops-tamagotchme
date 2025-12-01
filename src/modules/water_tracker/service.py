"""Water tracker service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...shared.base_service import BaseTrackerService
from .models import WaterEntry
from ...shared.database_interface import BaseRepository

logger = logging.getLogger(__name__)


class WaterTrackerService(BaseTrackerService):
    """Service for water intake tracking."""

    def __init__(self, db_session: Session):
        """Initialize water tracker service."""
        super().__init__(db_session)
        self.repository = BaseRepository(db_session, WaterEntry)

    def log_water(self, user_id: int, amount_ml: float, timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Log water intake.
        
        Args:
            user_id: User's ID
            amount_ml: Amount of water in milliliters
            timestamp: When the water was consumed (defaults to now)
            
        Returns:
            Created water entry
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_date()
            
            entry = self.repository.create(
                user_id=user_id,
                amount_ml=amount_ml,
                timestamp=timestamp
            )
            
            logger.info(f"Water logged for user {user_id}: {amount_ml}ml")
            return entry.to_dict() if entry else {}
            
        except Exception as e:
            self._handle_error("log_water", e)

    def get_daily_summary(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get daily water intake summary.
        
        Args:
            user_id: User's ID
            date: Date to get summary for (defaults to today)
            
        Returns:
            Dictionary with daily water summary
        """
        try:
            if date is None:
                date = self._get_current_date()
            
            # Get start and end of day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Query total water for the day
            total_ml = self.db_session.query(func.sum(WaterEntry.amount_ml)).filter(
                WaterEntry.user_id == user_id,
                WaterEntry.timestamp >= start_of_day,
                WaterEntry.timestamp < end_of_day
            ).scalar() or 0.0
            
            # Count entries
            entry_count = self.db_session.query(func.count(WaterEntry.id)).filter(
                WaterEntry.user_id == user_id,
                WaterEntry.timestamp >= start_of_day,
                WaterEntry.timestamp < end_of_day
            ).scalar() or 0
            
            return {
                "date": self._format_date(date),
                "total_ml": float(total_ml),
                "entry_count": entry_count,
                "total_liters": round(float(total_ml) / 1000, 2)
            }
            
        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(self, user_id: int, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get weekly water intake summary.
        
        Args:
            user_id: User's ID
            start_date: Start of week (defaults to 7 days ago)
            
        Returns:
            Dictionary with weekly water summary
        """
        try:
            if start_date is None:
                start_date = self._get_current_date() - timedelta(days=7)
            
            end_date = start_date + timedelta(days=7)
            
            # Query total water for the week
            total_ml = self.db_session.query(func.sum(WaterEntry.amount_ml)).filter(
                WaterEntry.user_id == user_id,
                WaterEntry.timestamp >= start_date,
                WaterEntry.timestamp < end_date
            ).scalar() or 0.0
            
            # Daily average
            daily_average = float(total_ml) / 7
            
            return {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date),
                "total_ml": float(total_ml),
                "daily_average_ml": round(daily_average, 2),
                "total_liters": round(float(total_ml) / 1000, 2)
            }
            
        except Exception as e:
            self._handle_error("get_weekly_summary", e)

    def get_status(self) -> Dict[str, Any]:
        """Get water tracker service status."""
        try:
            total_entries = self.repository.count()
            return {
                "service": self.service_name,
                "status": "operational",
                "total_entries": total_entries
            }
        except Exception as e:
            return {
                "service": self.service_name,
                "status": "error",
                "error": str(e)
            }

    def get_entries_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get water entries within a date range.
        
        Args:
            user_id: User's ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of water entries
        """
        try:
            entries = self.db_session.query(WaterEntry).filter(
                WaterEntry.user_id == user_id,
                WaterEntry.timestamp >= start_date,
                WaterEntry.timestamp <= end_date
            ).order_by(WaterEntry.timestamp.desc()).all()
            
            return [entry.to_dict() for entry in entries]
            
        except Exception as e:
            self._handle_error("get_entries_by_date_range", e)
