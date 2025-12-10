# python
"""Gym tracker repository."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...shared.database_interface import BaseRepository
from .models import WorkoutEntry, StrengthExercise, WorkoutType

logger = logging.getLogger(__name__)


class GymRepository(BaseRepository):
    """Repository for gym tracker operations."""

    def __init__(self, db_session: Session):
        """Initialize with WorkoutEntry as the primary model."""
        super().__init__(db_session, WorkoutEntry)

    def create_workout_with_exercises(
            self,
            workout_data: Dict[str, Any],
            exercises: Optional[List[Dict[str, Any]]] = None
    ) -> WorkoutEntry:
        """Create a workout entry with optional strength exercises."""
        try:
            workout = WorkoutEntry(**workout_data)
            self.db_session.add(workout)
            self.db_session.flush()  # Get the ID without committing

            if exercises and workout.workout_type == WorkoutType.STRENGTH:
                for ex_data in exercises:
                    exercise = StrengthExercise(workout_id=workout.id, **ex_data)
                    self.db_session.add(exercise)

            self.db_session.commit()
            self.db_session.refresh(workout)

            logger.info("Created workout with id: %s", workout.id)
            return workout

        except Exception as e:
            self.db_session.rollback()
            logger.error("Failed to create workout with exercises: %s", e)
            raise

    def get_workouts_by_type(
            self,
            workout_type: WorkoutType,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None
    ) -> List[WorkoutEntry]:
        """Get workouts filtered by type and optional date range."""
        try:
            query = self.db_session.query(WorkoutEntry).filter(
                WorkoutEntry.workout_type == workout_type
            )

            if start_date:
                query = query.filter(WorkoutEntry.created_at >= start_date)
            if end_date:
                query = query.filter(WorkoutEntry.created_at <= end_date)

            return query.order_by(WorkoutEntry.created_at.desc()).all()

        except Exception as e:
            logger.error("Failed to get workouts by type: %s", e)
            raise

    def get_daily_workouts(self, date: datetime) -> List[WorkoutEntry]:
        """Get all workouts for a specific day."""
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = start + timedelta(days=1)
        return self.filter_by_date_range(start, end)

    def get_weekly_stats(
            self,
            start_date: datetime
    ) -> Dict[str, Any]:
        """Get aggregated weekly statistics."""
        try:
            end_date = start_date + timedelta(days=7)

            # Aggregate by workout type
            stats = self.db_session.query(
                WorkoutEntry.workout_type,
                func.count(WorkoutEntry.id).label('count'),
                func.sum(WorkoutEntry.duration_minutes).label('total_duration'),
                func.sum(WorkoutEntry.calories_burned).label('total_calories'),
                func.sum(WorkoutEntry.distance_km).label('total_distance')
            ).filter(
                WorkoutEntry.created_at >= start_date,
                WorkoutEntry.created_at < end_date
            ).group_by(WorkoutEntry.workout_type).all()

            result = {}
            for stat in stats:
                # preserve 0 vs None correctly for distance
                result[stat.workout_type.value] = {
                    'count': stat.count,
                    'total_duration_minutes': int(stat.total_duration or 0),
                    'total_calories': float(stat.total_calories or 0),
                    'total_distance_km': float(stat.total_distance) if stat.total_distance is not None else None
                }

            return result

        except Exception as e:
            logger.error("Failed to get weekly stats: %s", e)
            raise

    def get_strength_exercises_for_workout(self, workout_id: int) -> List[StrengthExercise]:
        """Get all strength exercises for a specific workout."""
        try:
            return self.db_session.query(StrengthExercise).filter(
                StrengthExercise.workout_id == workout_id
            ).all()
        except Exception as e:
            logger.error("Failed to get strength exercises: %s", e)
            raise
