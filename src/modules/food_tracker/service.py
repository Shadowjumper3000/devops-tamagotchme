"""Food tracker service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from ...shared.base_service import BaseTrackerService
from ...shared.database_interface import BaseRepository
from .models import FoodEntry

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
        meal_type: Optional[str] = None,
        protein: Optional[float] = 0.0,
        carbs: Optional[float] = 0.0,
        fats: Optional[float] = 0.0,
    ) -> Dict[str, Any]:
        """
        Log food/meal entry.

        Args:
            user_id: User's ID
            calories: Calorie amount
            timestamp: When the meal was consumed (defaults to now)
            meal_name: Optional meal description
            meal_type: Optional meal type (breakfast, lunch, dinner, snack)
            protein: Protein amount in grams (defaults to 0)
            carbs: Carbohydrate amount in grams (defaults to 0)
            fats: Fat amount in grams (defaults to 0)

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
                meal_type=meal_type,
                protein=protein,
                carbs=carbs,
                fats=fats,
            )

            logger.info(f"Food logged for user {user_id}: {calories} calories")
            return entry.to_dict() if entry else {}

        except Exception as e:
            self._handle_error("log_food", e)

    def get_daily_summary(
        self, user_id: int, date: Optional[datetime] = None
    ) -> Dict[str, Any]:
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
            total_calories = (
                self.db_session.query(func.sum(FoodEntry.calories))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .scalar()
                or 0.0
            )

            # Query total macronutrients for the day
            total_protein = (
                self.db_session.query(func.sum(FoodEntry.protein))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .scalar()
                or 0.0
            )

            total_carbs = (
                self.db_session.query(func.sum(FoodEntry.carbs))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .scalar()
                or 0.0
            )

            total_fats = (
                self.db_session.query(func.sum(FoodEntry.fats))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .scalar()
                or 0.0
            )

            # Count meals
            meal_count = (
                self.db_session.query(func.count(FoodEntry.id))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .scalar()
                or 0
            )

            # Get breakdown by meal type
            meal_breakdown = {}
            for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                type_calories = (
                    self.db_session.query(func.sum(FoodEntry.calories))
                    .filter(
                        FoodEntry.user_id == user_id,
                        FoodEntry.timestamp >= start_of_day,
                        FoodEntry.timestamp < end_of_day,
                        FoodEntry.meal_type == meal_type,
                    )
                    .scalar()
                    or 0.0
                )
                meal_breakdown[meal_type] = float(type_calories)

            # Get individual meals for the day
            meals = (
                self.db_session.query(FoodEntry)
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_of_day,
                    FoodEntry.timestamp < end_of_day,
                )
                .order_by(FoodEntry.timestamp.asc())
                .all()
            )

            meals_list = [
                {
                    "name": meal.meal_name or meal.meal_type or "Meal",
                    "calories": float(meal.calories),
                }
                for meal in meals
            ]

            return {
                "date": self._format_date(date),
                "total_calories": float(total_calories),
                "total_protein": float(total_protein),
                "total_carbs": float(total_carbs),
                "total_fats": float(total_fats),
                "entry_count": meal_count,
                "meal_breakdown": meal_breakdown,
                "meals": meals_list,
            }

        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(
        self, user_id: int, date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get weekly calorie intake summary for the 7 days leading up to the given date.

        Args:
            user_id: User's ID
            date: End date of the week (defaults to today, looks back 7 days)

        Returns:
            Dictionary with weekly food summary
        """
        try:
            if date is None:
                date = self._get_current_date()

            # Look back 7 days from the given date
            start_date = date - timedelta(days=6)
            end_date = date + timedelta(days=1)  # Include the end date itself

            # Query total calories for the week
            total_calories = (
                self.db_session.query(func.sum(FoodEntry.calories))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp < end_date,
                )
                .scalar()
                or 0.0
            )

            # Query total macronutrients for the week
            total_protein = (
                self.db_session.query(func.sum(FoodEntry.protein))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp < end_date,
                )
                .scalar()
                or 0.0
            )

            total_carbs = (
                self.db_session.query(func.sum(FoodEntry.carbs))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp < end_date,
                )
                .scalar()
                or 0.0
            )

            total_fats = (
                self.db_session.query(func.sum(FoodEntry.fats))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp < end_date,
                )
                .scalar()
                or 0.0
            )

            # Daily averages
            daily_average = float(total_calories) / 7

            # Total meals
            total_meals = (
                self.db_session.query(func.count(FoodEntry.id))
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp < end_date,
                )
                .scalar()
                or 0
            )

            return {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date),
                "total_calories": float(total_calories),
                "average_daily_calories": round(daily_average, 2),
                "average_daily_protein": round(float(total_protein) / 7, 2),
                "average_daily_carbs": round(float(total_carbs) / 7, 2),
                "average_daily_fats": round(float(total_fats) / 7, 2),
                "entry_count": total_meals,
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
                "total_entries": total_entries,
            }
        except Exception as e:
            return {"service": self.service_name, "status": "error", "error": str(e)}

    def get_entries_by_date_range(
        self, user_id: int, start_date: datetime, end_date: datetime
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
            entries = (
                self.db_session.query(FoodEntry)
                .filter(
                    FoodEntry.user_id == user_id,
                    FoodEntry.timestamp >= start_date,
                    FoodEntry.timestamp <= end_date,
                )
                .order_by(FoodEntry.timestamp.desc())
                .all()
            )

            return [entry.to_dict() for entry in entries]

        except Exception as e:
            self._handle_error("get_entries_by_date_range", e)

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete a food entry by ID.

        Args:
            entry_id: ID of the entry to delete

        Returns:
            True if deleted successfully, False if not found
        """
        try:
            result = self.repository.delete(entry_id)
            if result:
                logger.info(f"Food entry {entry_id} deleted successfully")
            else:
                logger.warning(f"Food entry {entry_id} not found for deletion")
            return result
        except Exception as e:
            self._handle_error("delete_entry", e)

    def update_entry(
        self,
        entry_id: int,
        calories: Optional[float] = None,
        meal_name: Optional[str] = None,
        meal_type: Optional[str] = None,
        protein: Optional[float] = None,
        carbs: Optional[float] = None,
        fats: Optional[float] = None,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Update a food entry.

        Args:
            entry_id: ID of the entry to update
            calories: Updated calorie amount
            meal_name: Updated meal name
            meal_type: Updated meal type
            protein: Updated protein amount
            carbs: Updated carbs amount
            fats: Updated fats amount
            timestamp: Updated timestamp

        Returns:
            Updated food entry dictionary
        """
        try:
            # Build update dict with only provided values
            update_data = {}
            if calories is not None:
                update_data["calories"] = calories
            if meal_name is not None:
                update_data["meal_name"] = meal_name
            if meal_type is not None:
                update_data["meal_type"] = meal_type
            if protein is not None:
                update_data["protein"] = protein
            if carbs is not None:
                update_data["carbs"] = carbs
            if fats is not None:
                update_data["fats"] = fats
            if timestamp is not None:
                update_data["timestamp"] = timestamp

            entry = self.repository.update(entry_id, **update_data)

            if not entry:
                logger.warning(f"Food entry {entry_id} not found for update")
                return {}

            logger.info(f"Food entry {entry_id} updated successfully")
            return entry.to_dict()

        except Exception as e:
            self._handle_error("update_entry", e)

    def get_entries_by_meal_type(
        self,
        user_id: int,
        meal_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get food entries filtered by meal type.

        Args:
            user_id: User's ID
            meal_type: Meal type to filter by (breakfast, lunch, dinner, snack)
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of food entries matching meal type
        """
        try:
            query = self.db_session.query(FoodEntry).filter(
                FoodEntry.user_id == user_id, FoodEntry.meal_type == meal_type
            )

            if start_date:
                query = query.filter(FoodEntry.timestamp >= start_date)
            if end_date:
                query = query.filter(FoodEntry.timestamp <= end_date)

            entries = query.order_by(FoodEntry.timestamp.desc()).all()
            return [entry.to_dict() for entry in entries]

        except Exception as e:
            self._handle_error("get_entries_by_meal_type", e)

    def get_calories_by_meal_type(
        self, user_id: int, date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get calorie totals grouped by meal type for a specific date.

        Args:
            user_id: User's ID
            date: Date to query (defaults to today)

        Returns:
            Dictionary mapping meal types to calorie totals
        """
        try:
            if date is None:
                date = self._get_current_date()

            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            breakdown = {}
            for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
                total = (
                    self.db_session.query(func.sum(FoodEntry.calories))
                    .filter(
                        FoodEntry.user_id == user_id,
                        FoodEntry.timestamp >= start_of_day,
                        FoodEntry.timestamp < end_of_day,
                        FoodEntry.meal_type == meal_type,
                    )
                    .scalar()
                    or 0.0
                )
                breakdown[meal_type] = float(total)

            return breakdown

        except Exception as e:
            self._handle_error("get_calories_by_meal_type", e)
