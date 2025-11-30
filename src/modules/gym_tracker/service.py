"""Gym tracker service."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from ...shared.base_service import BaseTrackerService
from .repository import GymRepository
from .models import WorkoutType

logger = logging.getLogger(__name__)


class GymTrackerService(BaseTrackerService):
    """Service for managing gym tracking functionality."""

    def __init__(self, db_session):
        """Initialize service with database session."""
        super().__init__(db_session)
        self.repository = GymRepository(db_session)

    def log_workout(
        self,
        name: str,
        workout_type: str,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None,
        notes: Optional[str] = None,
        strength_exercises: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Log a new workout."""
        try:
            workout_type_enum = WorkoutType(workout_type)

            workout_data = {
                'name': name,
                'workout_type': workout_type_enum,
                'duration_minutes': duration_minutes,
                'calories_burned': calories_burned,
                'distance_km': distance_km,
                'notes': notes
            }

            workout = self.repository.create_workout_with_exercises(
                workout_data,
                strength_exercises
            )

            return self._format_workout(workout)

        except Exception as e:
            self._handle_error("log_workout", e)

    def get_workout(self, workout_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific workout by ID."""
        try:
            workout = self.repository.get_by_id(workout_id)
            return self._format_workout(workout) if workout else None
        except Exception as e:
            self._handle_error("get_workout", e)

    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get daily workout summary per contract."""
        try:
            target_date = date or self._get_current_date()
            workouts = self.repository.get_daily_workouts(target_date)

            return {
                'date': self._format_date(target_date),
                'workouts': [
                    {
                        'type': w.workout_type.value,
                        'name': w.name,
                        'duration_minutes': w.duration_minutes,
                        'calories_burned': w.calories_burned
                    }
                    for w in workouts
                ]
            }

        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(
        self,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get weekly workout summary per contract."""
        try:
            target_start = start_date or (self._get_current_date() - timedelta(days=7))
            stats = self.repository.get_weekly_stats(target_start)

            return {
                'start_date': self._format_date(target_start),
                'end_date': self._format_date(target_start + timedelta(days=7)),
                'weekly_workouts': [
                    {
                        'type': workout_type,
                        'total_duration_minutes': data['total_duration_minutes'],
                        'total_calories': data['total_calories'],
                        'workout_count': data['count']
                    }
                    for workout_type, data in stats.items()
                ]
            }

        except Exception as e:
            self._handle_error("get_weekly_summary", e)

    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        try:
            total_workouts = self.repository.count()
            recent = self.repository.get_recent(1)

            return {
                'total_workouts': total_workouts,
                'last_workout': self._format_workout(recent[0]) if recent else None,
                'service_status': 'active'
            }

        except Exception as e:
            logger.error("Error getting status: %s", e)
            return {'service_status': 'error', 'error': str(e)}

    def query_workouts(
        self,
        workout_type: Optional[str] = None,
        min_duration: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Query workouts with filters (for mock query support)."""
        try:
            if workout_type:
                workouts = self.repository.get_workouts_by_type(
                    WorkoutType(workout_type),
                    start_date,
                    end_date
                )
            else:
                workouts = self.repository.filter_by_date_range(start_date, end_date)

            # Filter by duration if specified
            if min_duration:
                workouts = [w for w in workouts if w.duration_minutes > min_duration]

            return [self._format_workout(w) for w in workouts]

        except Exception as e:
            self._handle_error("query_workouts", e)

    def _format_workout(self, workout) -> Dict[str, Any]:
        """Format workout for API response."""
        if not workout:
            return {}

        formatted = {
            'id': workout.id,
            'name': workout.name,
            'type': workout.workout_type.value,
            'duration_minutes': workout.duration_minutes,
            'calories_burned': workout.calories_burned,
            'distance_km': workout.distance_km,
            'notes': workout.notes,
            'created_at': workout.created_at.isoformat()
        }

        # Add strength exercises if available
        if workout.strength_exercises:
            formatted['strength_exercises'] = [
                {
                    'exercise_name': ex.exercise_name,
                    'sets': ex.sets,
                    'reps': ex.reps,
                    'weight_kg': ex.weight_kg,
                    'volume': ex.volume
                }
                for ex in workout.strength_exercises
            ]

        return formatted
