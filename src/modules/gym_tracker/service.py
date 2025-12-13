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
        user_id: int,
        name: str,
        workout_type: str,
        duration_minutes: int,
        calories_burned: Optional[float] = None,
        distance_km: Optional[float] = None,
        notes: Optional[str] = None,
        intensity: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        strength_exercises: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Log a new workout and return full formatted workout."""
        try:
            workout_type_enum = WorkoutType(workout_type.lower())

            workout_data = {
                'user_id': user_id,
                'name': name,
                'workout_type': workout_type_enum,
                'duration_minutes': duration_minutes,
                'calories_burned': calories_burned,
                'distance_km': distance_km,
                'notes': notes,
                'intensity': intensity,
                'created_at': timestamp or datetime.now()
            }

            workout = self.repository.create_workout_with_exercises(
                workout_data,
                strength_exercises
            )

            return self._format_workout(workout)

        except Exception as e:
            self._handle_error("log_workout", e)

    # Frontend compatibility methods
    def log_cardio_workout(
        self,
        user_id: int,
        cardio_type: str,
        duration_minutes: int,
        distance_km: float = 0,
        intensity: str = "Medium",
        calories: int = 0,
        notes: str = "",
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Log cardio workout (frontend compatibility)."""
        return self.log_workout(
            user_id=user_id,
            name=cardio_type.capitalize(),
            workout_type="cardio",
            duration_minutes=duration_minutes,
            distance_km=distance_km if distance_km > 0 else None,
            intensity=intensity,
            calories_burned=float(calories) if calories > 0 else None,
            notes=notes,
            timestamp=timestamp
        )

    def get_entries_by_date_range(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get entries by date range (frontend compatibility)."""
        try:
            workouts = self.repository.get_by_user_and_date_range(user_id, start_date, end_date)
            return [self._format_workout(w) for w in workouts]
        except Exception as e:
            self._handle_error("get_entries_by_date_range", e)

    def delete_entry(self, workout_id: int):
        """Delete entry (frontend compatibility - needs user_id)."""
        # Note: This is incomplete without user_id, frontend should pass it
        try:
            self.repository.delete(workout_id)
        except Exception as e:
            self._handle_error("delete_entry", e)

    def get_workout(self, user_id: int, workout_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific workout by ID (contract-compliant)."""
        try:
            workout = self.repository.get_by_user_and_id(user_id, workout_id)
            if not workout:
                return None
            return {'workout': self._to_contract_workout(workout)}
        except Exception as e:
            self._handle_error("get_workout", e)

    def get_daily_summary(self, user_id: int, date: Optional[datetime] = None) -> Dict[str, Any]:
        """Return contract-compliant daily summary."""
        try:
            target_date = date or self._get_current_date()
            workouts = self.repository.get_daily_workouts(user_id, target_date)

            # Contract format
            contract_response = {
                'workouts': [
                    {
                        'type': w.workout_type.value,
                        'duration_minutes': w.duration_minutes
                    }
                    for w in workouts
                ]
            }

            # Frontend compatibility - add aggregated stats
            total_cardio = sum(w.duration_minutes for w in workouts if w.workout_type == WorkoutType.CARDIO)
            total_calories = sum(w.calories_burned or 0 for w in workouts)

            contract_response['total_cardio_minutes'] = total_cardio
            contract_response['estimated_calories'] = int(total_calories)

            return contract_response

        except Exception as e:
            self._handle_error("get_daily_summary", e)

    def get_weekly_summary(
        self,
        user_id: int,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Return contract-compliant weekly summary."""
        try:
            target_start = start_date or (self._get_current_date() - timedelta(days=7))
            stats = self.repository.get_weekly_stats(user_id, target_start)

            # Contract format
            contract_response = {
                'weekly_workouts': [
                    {
                        'type': workout_type,
                        'total_duration_minutes': data['total_duration_minutes']
                    }
                    for workout_type, data in stats.items()
                ]
            }

            # Frontend compatibility
            cardio_stats = stats.get('cardio', {})
            contract_response['total_cardio_minutes'] = cardio_stats.get('total_duration_minutes', 0)
            contract_response['workout_count'] = sum(data['count'] for data in stats.values())

            return contract_response

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
        user_id: int,
        workout_type: Optional[str] = None,
        min_duration: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Query workouts with filters."""
        try:
            if workout_type:
                workouts = self.repository.get_workouts_by_type(
                    user_id,
                    WorkoutType(workout_type),
                    start_date,
                    end_date
                )
            else:
                workouts = self.repository.get_by_user_and_date_range(user_id, start_date, end_date)

            if min_duration is not None:
                workouts = [w for w in workouts if w.duration_minutes > min_duration]

            return [self._format_workout(w) for w in workouts]

        except Exception as e:
            self._handle_error("query_workouts", e)

    def mock_query(self, user_id: int, query_text: str, workout_type: Optional[str] = None, min_duration: Optional[int] = None) -> Dict[str, Any]:
        """Return the mock-query contract."""
        try:
            results = self.query_workouts(user_id=user_id, workout_type=workout_type, min_duration=min_duration)
            trimmed = [
                {
                    'type': r.get('type'),
                    'duration_minutes': r.get('duration_minutes'),
                    'calories_burned': r.get('calories_burned')
                }
                for r in results
            ]
            return {'query': query_text, 'results': trimmed}
        except Exception as e:
            self._handle_error("mock_query", e)

    def _to_contract_workout(self, workout) -> Dict[str, Any]:
        """Return the minimal contract fields for an individual workout."""
        return {
            'type': workout.workout_type.value,
            'duration_minutes': workout.duration_minutes,
            'calories_burned': workout.calories_burned
        }

    def _format_workout(self, workout) -> Dict[str, Any]:
        """Format workout for API response (full form)."""
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
            'intensity': workout.intensity,
            'created_at': workout.created_at.isoformat()
        }

        if getattr(workout, 'strength_exercises', None):
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
