"""Gym tracker service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...shared.base_service import BaseTrackerService
from .models import WorkoutEntry
from ...shared.database_interface import BaseRepository

logger = logging.getLogger(__name__)


class GymTrackerService(BaseTrackerService):
    """Service for gym workout tracking."""

    def __init__(self, db_session: Session):
        """Initialize gym tracker service."""
        super().__init__(db_session)
        self.repository = BaseRepository(db_session, WorkoutEntry)

    def log_hiit_workout(
        self,
        user_id: int,
        exercises: List[Dict[str, Any]],
        timestamp: Optional[datetime] = None,
        notes: Optional[str] = None,
        intensity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a HIIT workout.
        
        Args:
            user_id: User's ID
            exercises: List of exercises with format [{"exercise": "Push-ups", "reps": 20, "weight": 0}, ...]
            timestamp: When the workout was performed (defaults to now)
            notes: Optional workout notes
            intensity: Optional intensity level (low, medium, high)
            
        Returns:
            Created workout entry
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_date()
            
            entry = WorkoutEntry(
                user_id=user_id,
                workout_type="HIIT",
                timestamp=timestamp,
                notes=notes,
                intensity=intensity
            )
            entry.set_exercises_list(exercises)
            
            self.db_session.add(entry)
            self.db_session.commit()
            self.db_session.refresh(entry)
            
            logger.info(f"HIIT workout logged for user {user_id}")
            return entry.to_dict()
            
        except Exception as e:
            self._handle_error("log_hiit_workout", e)

    def log_cardio_workout(
        self,
        user_id: int,
        exercise_name: str,
        duration_minutes: float,
        timestamp: Optional[datetime] = None,
        notes: Optional[str] = None,
        intensity: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Log a Cardio workout.
        
        Args:
            user_id: User's ID
            exercise_name: Name of cardio exercise (running, cycling, etc.)
            duration_minutes: Duration in minutes
            timestamp: When the workout was performed (defaults to now)
            notes: Optional workout notes
            intensity: Optional intensity level (low, medium, high)
            
        Returns:
            Created workout entry
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_date()
            
            entry = self.repository.create(
                user_id=user_id,
                workout_type="Cardio",
                exercise_name=exercise_name,
                duration_minutes=duration_minutes,
                timestamp=timestamp,
                notes=notes,
                intensity=intensity
            )
            
            logger.info(f"Cardio workout logged for user {user_id}: {exercise_name} for {duration_minutes} min")
            return entry.to_dict() if entry else {}
            
        except Exception as e:
            self._handle_error("log_cardio_workout", e)

    def get_daily_summary(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get daily workout summary.
        
        Args:
            user_id: User's ID
            date: Date to get summary for (defaults to today)
            
        Returns:
            Dictionary with daily workout summary
        """
        try:
            if date is None:
                date = self._get_current_date()
            
            # Get start and end of day
            start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Query workouts for the day
            workouts = self.db_session.query(WorkoutEntry).filter(
                WorkoutEntry.user_id == user_id,
                WorkoutEntry.timestamp >= start_of_day,
                WorkoutEntry.timestamp < end_of_day
            ).all()
            
            workout_count = len(workouts)
            hiit_count = sum(1 for w in workouts if w.workout_type == "HIIT")
            cardio_count = sum(1 for w in workouts if w.workout_type == "Cardio")
            
            # Calculate total cardio duration
            total_cardio_minutes = sum(
                w.duration_minutes for w in workouts 
                if w.workout_type == "Cardio" and w.duration_minutes
            ) or 0.0
            
            return {
                "date": self._format_date(date),
                "workout_count": workout_count,
                "hiit_count": hiit_count,
                "cardio_count": cardio_count,
                "total_cardio_minutes": float(total_cardio_minutes),
                "workouts": [w.to_dict() for w in workouts]
            }
            
        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(self, user_id: int, start_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get weekly workout summary.
        
        Args:
            user_id: User's ID
            start_date: Start of week (defaults to 7 days ago)
            
        Returns:
            Dictionary with weekly workout summary
        """
        try:
            if start_date is None:
                start_date = self._get_current_date() - timedelta(days=7)
            
            end_date = start_date + timedelta(days=7)
            
            # Query workouts for the week
            workouts = self.db_session.query(WorkoutEntry).filter(
                WorkoutEntry.user_id == user_id,
                WorkoutEntry.timestamp >= start_date,
                WorkoutEntry.timestamp < end_date
            ).all()
            
            total_workouts = len(workouts)
            hiit_count = sum(1 for w in workouts if w.workout_type == "HIIT")
            cardio_count = sum(1 for w in workouts if w.workout_type == "Cardio")
            
            # Calculate total cardio duration
            total_cardio_minutes = sum(
                w.duration_minutes for w in workouts 
                if w.workout_type == "Cardio" and w.duration_minutes
            ) or 0.0
            
            # Days with workouts
            unique_dates = len(set(w.timestamp.date() for w in workouts))
            
            return {
                "start_date": self._format_date(start_date),
                "end_date": self._format_date(end_date),
                "total_workouts": total_workouts,
                "hiit_count": hiit_count,
                "cardio_count": cardio_count,
                "total_cardio_minutes": float(total_cardio_minutes),
                "active_days": unique_dates
            }
            
        except Exception as e:
            self._handle_error("get_weekly_summary", e)

    def get_status(self) -> Dict[str, Any]:
        """Get gym tracker service status."""
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
        Get workout entries within a date range.
        
        Args:
            user_id: User's ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of workout entries
        """
        try:
            entries = self.db_session.query(WorkoutEntry).filter(
                WorkoutEntry.user_id == user_id,
                WorkoutEntry.timestamp >= start_date,
                WorkoutEntry.timestamp <= end_date
            ).order_by(WorkoutEntry.timestamp.desc()).all()
            
            return [entry.to_dict() for entry in entries]
            
        except Exception as e:
            self._handle_error("get_entries_by_date_range", e)
