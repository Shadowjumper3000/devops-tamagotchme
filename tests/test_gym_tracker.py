"""Unit tests for Gym Tracker Service."""

import pytest
from datetime import datetime, timedelta
from src.modules.gym_tracker.service import GymTrackerService


class TestGymTrackerService:
    """Test suite for GymTrackerService."""

    @pytest.fixture
    def gym_service(self, db_session):
        """Create a gym tracker service instance."""
        return GymTrackerService(db_session)

    def test_log_hiit_workout(self, gym_service, sample_user):
        """Test logging HIIT workout."""
        exercises = [
            {"exercise": "Push-ups", "reps": 20, "weight": 0},
            {"exercise": "Squats", "reps": 30, "weight": 0},
            {"exercise": "Burpees", "reps": 15, "weight": 0}
        ]
        
        result = gym_service.log_hiit_workout(
            user_id=sample_user.id,
            exercises=exercises,
            notes="Great workout!",
            intensity="high"
        )
        
        assert result is not None
        assert result["user_id"] == sample_user.id
        assert result["workout_type"] == "HIIT"
        assert len(result["exercises"]) == 3
        assert result["intensity"] == "high"

    def test_log_cardio_workout(self, gym_service, sample_user):
        """Test logging cardio workout."""
        result = gym_service.log_cardio_workout(
            user_id=sample_user.id,
            cardio_type="running",
            duration_minutes=30,
            distance_km=5.0,
            notes="Morning run"
        )
        
        assert result["workout_type"] == "Cardio"
        assert result["cardio_type"] == "running"
        assert result["duration_minutes"] == 30
        assert result["distance_km"] == 5.0

    def test_log_strength_workout(self, gym_service, sample_user):
        """Test logging strength training workout."""
        exercises = [
            {"exercise": "Bench Press", "sets": 3, "reps": 10, "weight": 80},
            {"exercise": "Deadlift", "sets": 3, "reps": 8, "weight": 100}
        ]
        
        result = gym_service.log_strength_workout(
            user_id=sample_user.id,
            exercises=exercises,
            notes="Leg day"
        )
        
        assert result["workout_type"] == "Strength"
        assert len(result["exercises"]) == 2

    def test_get_daily_summary(self, gym_service, sample_user, fixed_datetime):
        """Test getting daily gym summary."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        
        gym_service.log_hiit_workout(sample_user.id, exercises, fixed_datetime)
        gym_service.log_cardio_workout(sample_user.id, "running", 30, 5.0, fixed_datetime)
        
        summary = gym_service.get_daily_summary(sample_user.id, fixed_datetime)
        
        assert summary["workout_count"] == 2
        assert summary["total_cardio_minutes"] == 30

    def test_get_weekly_summary(self, gym_service, sample_user, fixed_datetime):
        """Test getting weekly gym summary."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        
        # Log workouts across multiple days
        for i in range(7):
            date = fixed_datetime - timedelta(days=i)
            gym_service.log_hiit_workout(sample_user.id, exercises, date)
        
        summary = gym_service.get_weekly_summary(sample_user.id, fixed_datetime)
        
        assert summary["workout_count"] == 7
        assert summary["days_active"] == 7

    def test_update_workout(self, gym_service, sample_user):
        """Test updating a workout entry."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        entry = gym_service.log_hiit_workout(sample_user.id, exercises)
        entry_id = entry["id"]
        
        updated_exercises = [{"exercise": "Push-ups", "reps": 25, "weight": 0}]
        updated = gym_service.update_entry(
            entry_id=entry_id,
            exercises=updated_exercises,
            notes="Improved reps!"
        )
        
        assert updated["exercises"][0]["reps"] == 25
        assert updated["notes"] == "Improved reps!"

    def test_delete_workout(self, gym_service, sample_user):
        """Test deleting a workout entry."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        entry = gym_service.log_hiit_workout(sample_user.id, exercises)
        entry_id = entry["id"]
        
        result = gym_service.delete_entry(entry_id)
        
        assert result is True

    def test_get_workouts_by_type(self, gym_service, sample_user, fixed_datetime):
        """Test filtering workouts by type."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        
        gym_service.log_hiit_workout(sample_user.id, exercises, fixed_datetime)
        gym_service.log_cardio_workout(sample_user.id, "running", 30, 5.0, fixed_datetime)
        gym_service.log_strength_workout(sample_user.id, exercises, fixed_datetime)
        
        hiit_workouts = gym_service.get_workouts_by_type(
            sample_user.id,
            "HIIT",
            fixed_datetime
        )
        
        assert len(hiit_workouts) == 1
        assert hiit_workouts[0]["workout_type"] == "HIIT"

    def test_workout_streak(self, gym_service, sample_user, fixed_datetime):
        """Test calculating workout streak."""
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        
        # Log consecutive workouts
        for i in range(5):
            date = fixed_datetime - timedelta(days=i)
            gym_service.log_hiit_workout(sample_user.id, exercises, date)
        
        streak = gym_service.get_workout_streak(sample_user.id, fixed_datetime)
        
        assert streak >= 5
