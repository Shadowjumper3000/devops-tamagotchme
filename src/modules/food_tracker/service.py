"""Food tracker service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...shared.base_service import BaseTrackerService
from .models import FoodEntry
from ...shared.database_interface import BaseRepository

logger = logging.getLogger(__name__)


class FoodTrackerService(BaseTrackerService):
    """Service for food and calorie tracking."""

    def __init__(self, db_session: Session):
        """Initialize food tracker service."""
        super().__init__(db_session)
        self.repository = BaseRepository(db_session, FoodEntry)

    def log_food(
        self,
        user_id: int,
        calories: float,
        timestamp: Optional[datetime] = None,
        meal_name: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log food/meal entry.
        
        Args:
            user_id: User's ID
            calories: Calorie amount
            timestamp: When the meal was consumed (defaults to now)
            meal_name: Optional meal description
            meal_type: Optional meal type (breakfast, lunch, dinner, snack)
            
        Returns:
            Created food entry
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_date()
            
            entry = self.repository.create(
                user_id=user_id,
                calories=calories,
                timestamp=timestamp,
                meal_name=meal_name,
                meal_type=meal_type
            )
            
            logger.info(f"Food logged for user {user_id}: {calories} calories")
            return entry.to_dict() if entry else {}
            
        except Exception as e:
            self._handle_error("log_food", e)

    def get_daily_summary(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get daily calorie intake summary.
        
        Args:
            user_id: User's ID
            date: Date to get summary for (defaults to today)
            
        Returns:
            Dictionary with daily food summary
        """
        try:
            if date is None:
                date = self._get_current_date()
            
            # Get start and end of day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Query total calories for the day
            total_calories = self.db_session.query(func.sum(FoodEntry.calories)).filter(
                FoodEntry.user_id == user_id,
                FoodEntry.timestamp >= start_of_day,
                FoodEntry.timestamp < end_of_day
            ).scalar() or 0.0
            
            # Count meals
            meal_count = self.db_session.query(func.count(FoodEntry.id)).filter(
                FoodEntry.user_id == user_id,
                FoodEntry.timestamp >= start_of_day,
                FoodEntry.timestamp < end_of_day
            ).scalar() or 0
            
            # Get breakdown by meal type
            meal_breakdown = {}
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                type_calories = self.db_session.query(func.sum(FoodEntry.calories)).filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                    FoodEntry.meal_type == meal_type
                ).scalar() or 0.0
                meal_breakdown[meal_type] = float(type_calories)
            
            return {
                "date": self._format_date(date),
                "total_calories": float(total_calories),
                "meal_count": meal_count,
                "meal_breakdown": meal_breakdown
            }
            
        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(self, user_id: int, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get weekly calorie intake summary.
        
        Args:
            user_id: User's ID
            start_date: Start of week (defaults to 7 days ago)
            
        Returns:
            Dictionary with weekly food summary
        """
        try:
            if start_date is None:
                start_date = self._get_current_date() - timedelta(days=7)
            
            end_date = start_date + timedelta(days=7)
            
            # Query total calories for the week
            total_calories = self.db_session.query(func.sum(FoodEntry.calories)).filter(
                FoodEntry.user_id == user_id,
                FoodEntry.timestamp >= start_date,
                FoodEntry.timestamp < end_date
            ).scalar() or 0.0
            
            # Daily average
            daily_average = float(total_calories) / 7
            
            # Total meals
            total_meals = self.db_session.query(func.count(FoodEntry.id)).filter(
                FoodEntry.user_id == user_id,
                FoodEntry.timestamp >= start_date,
                FoodEntry.timestamp < end_date
            ).scalar() or 0
            
            return {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date),
                "total_calories": float(total_calories),
                "daily_average_calories": round(daily_average, 2),
                "total_meals": total_meals
            }
            
        except Exception as e:
            self._handle_error("get_weekly_summary", e)

    def get_status(self) -> Dict[str, Any]:
        """Get food tracker service status."""
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
        Get food entries within a date range.
        
        Args:
            user_id: User's ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of food entries
        """
        try:
            entries = self.db_session.query(FoodEntry).filter(
                FoodEntry.user_id == user_id,
                FoodEntry.timestamp >= start_date,
                FoodEntry.timestamp <= end_date
            ).order_by(FoodEntry.timestamp.desc()).all()
            
            return [entry.to_dict() for entry in entries]
            
        except Exception as e:
            self._handle_error("get_entries_by_date_range", e)
