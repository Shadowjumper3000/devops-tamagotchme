"""Unit tests for Gym Tracker Service."""

import pytest
from datetime import datetime, timedelta
from src.modules.gym_tracker.service import GymTrackerService
from src.modules.gym_tracker.models import WorkoutType


class TestGymTrackerService:
    """Test suite for GymTrackerService."""

    @pytest.fixture
    def gym_service(self, db_session):
        """Create a gym tracker service instance."""
        return GymTrackerService(db_session)

    def test_log_workout_cardio(self, gym_service, sample_user):
        """Test logging cardio workout."""
        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Morning Run",
            workout_type="cardio",
            duration_minutes=30,
            distance_km=5.0,
            calories_burned=300.0,
            intensity="Medium",
            notes="Felt great!"
        )

        assert result is not None
        assert result["name"] == "Morning Run"
        assert result["type"] == "cardio"
        assert result["duration_minutes"] == 30
        assert result["distance_km"] == 5.0
        assert result["calories_burned"] == 300.0
        assert result["intensity"] == "Medium"

    def test_log_workout_strength(self, gym_service, sample_user):
        """Test logging strength training workout with exercises."""
        exercises = [
            {"exercise_name": "Bench Press", "sets": 3, "reps": 10, "weight_kg": 80.0},
            {"exercise_name": "Squats", "sets": 3, "reps": 12, "weight_kg": 100.0}
        ]

        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Upper Body Day",
            workout_type="strength",
            duration_minutes=45,
            calories_burned=400.0,
            intensity="High",
            strength_exercises=exercises
        )

        assert result["name"] == "Upper Body Day"
        assert result["type"] == "strength"
        assert result["duration_minutes"] == 45
        assert "strength_exercises" in result
        assert len(result["strength_exercises"]) == 2
        assert result["strength_exercises"][0]["exercise_name"] == "Bench Press"
        assert result["strength_exercises"][0]["volume"] == 2400.0  # 3 * 10 * 80

    def test_log_cardio_workout_compatibility(self, gym_service, sample_user):
        """Test frontend-compatible cardio logging method."""
        result = gym_service.log_cardio_workout(
            user_id=sample_user.id,
            cardio_type="running",
            duration_minutes=30,
            distance_km=5.0,
            intensity="Medium",
            calories=300,
            notes="Great run!"
        )

        assert result["name"] == "Running"
        assert result["type"] == "cardio"
        assert result["duration_minutes"] == 30
        assert result["distance_km"] == 5.0
        assert result["calories_burned"] == 300.0

    def test_get_daily_summary_contract(self, gym_service, sample_user, fixed_datetime):
        """Test getting daily summary in contract format."""
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Morning Cardio",
            workout_type="cardio",
            duration_minutes=30,
            timestamp=fixed_datetime
        )
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Evening Strength",
            workout_type="strength",
            duration_minutes=45,
            timestamp=fixed_datetime
        )

        summary = gym_service.get_daily_summary(sample_user.id, fixed_datetime)

        assert "workouts" in summary
        assert len(summary["workouts"]) == 2
        assert summary["workouts"][0]["type"] == "cardio"
        assert summary["workouts"][0]["duration_minutes"] == 30
        assert summary["total_cardio_minutes"] == 30

    def test_get_weekly_summary_contract(self, gym_service, sample_user, fixed_datetime):
        """Test getting weekly summary in contract format."""
        # Log workouts across multiple days
        for i in range(7):
            day = fixed_datetime + timedelta(days=i)
            gym_service.log_workout(
                user_id=sample_user.id,
                name=f"Cardio Day {i+1}",
                workout_type="cardio",
                duration_minutes=30,
                timestamp=day
            )

        summary = gym_service.get_weekly_summary(sample_user.id, fixed_datetime)

        assert "weekly_workouts" in summary
        assert len(summary["weekly_workouts"]) > 0
        assert summary["workout_count"] == 7
        cardio_workout = next((w for w in summary["weekly_workouts"] if w["type"] == "cardio"), None)
        assert cardio_workout is not None
        assert cardio_workout["total_duration_minutes"] == 210  # 7 days * 30 min

    def test_get_workout_individual(self, gym_service, sample_user):
        """Test getting individual workout (contract format)."""
        logged = gym_service.log_workout(
            user_id=sample_user.id,
            name="Test Workout",
            workout_type="cardio",
            duration_minutes=30,
            calories_burned=300.0
        )

        workout = gym_service.get_workout(sample_user.id, logged["id"])

        assert workout is not None
        assert "workout" in workout
        assert workout["workout"]["type"] == "cardio"
        assert workout["workout"]["duration_minutes"] == 30
        assert workout["workout"]["calories_burned"] == 300.0

    def test_query_workouts(self, gym_service, sample_user, fixed_datetime):
        """Test querying workouts with filters."""
        # Create multiple workouts
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Short Cardio",
            workout_type="cardio",
            duration_minutes=20,
            timestamp=fixed_datetime
        )
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Long Strength",
            workout_type="strength",
            duration_minutes=60,
            timestamp=fixed_datetime
        )
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Medium Cardio",
            workout_type="cardio",
            duration_minutes=35,
            timestamp=fixed_datetime
        )

        # Query strength workouts
        strength_workouts = gym_service.query_workouts(
            user_id=sample_user.id,
            workout_type="strength",
            start_date=fixed_datetime,
            end_date=fixed_datetime + timedelta(days=1)
        )

        assert len(strength_workouts) == 1
        assert strength_workouts[0]["type"] == "strength"

        # Query workouts longer than 40 minutes
        long_workouts = gym_service.query_workouts(
            user_id=sample_user.id,
            min_duration=40,
            start_date=fixed_datetime,
            end_date=fixed_datetime + timedelta(days=1)
        )

        assert len(long_workouts) == 1
        assert long_workouts[0]["duration_minutes"] == 60

    def test_mock_query(self, gym_service, sample_user, fixed_datetime):
        """Test mock query endpoint (contract format)."""
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Heavy Strength",
            workout_type="strength",
            duration_minutes=50,
            calories_burned=400.0,
            timestamp=fixed_datetime
        )

        result = gym_service.mock_query(
            user_id=sample_user.id,
            query_text="Get all strength workouts longer than 40 minutes",
            workout_type="strength",
            min_duration=40
        )

        assert "query" in result
        assert "results" in result
        assert result["query"] == "Get all strength workouts longer than 40 minutes"
        assert len(result["results"]) == 1
        assert result["results"][0]["type"] == "strength"
        assert result["results"][0]["duration_minutes"] == 50

    def test_get_entries_by_date_range(self, gym_service, sample_user, fixed_datetime):
        """Test getting entries by date range (frontend compatibility)."""
        start_date = fixed_datetime
        end_date = fixed_datetime + timedelta(days=3)

        for i in range(3):
            gym_service.log_workout(
                user_id=sample_user.id,
                name=f"Workout {i+1}",
                workout_type="cardio",
                duration_minutes=30,
                timestamp=fixed_datetime + timedelta(days=i)
            )

        entries = gym_service.get_entries_by_date_range(
            user_id=sample_user.id,
            start_date=start_date,
            end_date=end_date
        )

        assert len(entries) == 3
        assert all("name" in entry for entry in entries)

    def test_delete_workout(self, gym_service, sample_user):
        """Test deleting a workout entry."""
        logged = gym_service.log_workout(
            user_id=sample_user.id,
            name="Test Workout",
            workout_type="cardio",
            duration_minutes=30
        )

        result = gym_service.repository.delete_by_user_and_id(
            sample_user.id,
            logged["id"]
        )

        assert result is True

        # Verify it's deleted
        deleted = gym_service.get_workout(sample_user.id, logged["id"])
        assert deleted is None

    def test_workout_with_all_fields(self, gym_service, sample_user):
        """Test logging workout with all optional fields."""
        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Complete Workout",
            workout_type="cardio",
            duration_minutes=45,
            calories_burned=500.0,
            distance_km=7.5,
            notes="Personal best!",
            intensity="High"
        )

        assert result["name"] == "Complete Workout"
        assert result["duration_minutes"] == 45
        assert result["calories_burned"] == 500.0
        assert result["distance_km"] == 7.5
        assert result["notes"] == "Personal best!"
        assert result["intensity"] == "High"

    def test_get_status(self, gym_service, sample_user):
        """Test getting service status."""
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Test",
            workout_type="cardio",
            duration_minutes=30
        )

        status = gym_service.get_status()

        assert "total_workouts" in status
        assert "service_status" in status
        assert status["service_status"] == "active"
        assert status["total_workouts"] >= 1

    def test_multiple_workout_types(self, gym_service, sample_user, fixed_datetime):
        """Test logging different workout types."""
        workout_types = ["cardio", "strength", "flexibility", "sports"]

        for workout_type in workout_types:
            gym_service.log_workout(
                user_id=sample_user.id,
                name=f"{workout_type.capitalize()} Workout",
                workout_type=workout_type,
                duration_minutes=30,
                timestamp=fixed_datetime
            )

        summary = gym_service.get_daily_summary(sample_user.id, fixed_datetime)

        assert len(summary["workouts"]) == 4
        logged_types = {w["type"] for w in summary["workouts"]}
        assert logged_types == set(workout_types)

    def test_workout_timestamps(self, gym_service, sample_user, fixed_datetime):
        """Test that workouts maintain correct timestamps."""
        custom_time = fixed_datetime + timedelta(hours=5)

        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Timed Workout",
            workout_type="cardio",
            duration_minutes=30,
            timestamp=custom_time
        )

        created_at = datetime.fromisoformat(result["created_at"])
        assert created_at.date() == custom_time.date()
        assert created_at.hour == custom_time.hour

    def test_strength_workout_volume_calculation(self, gym_service, sample_user):
        """Test that strength exercise volume is calculated correctly."""
        exercises = [
            {"exercise_name": "Deadlift", "sets": 4, "reps": 5, "weight_kg": 150.0},
            {"exercise_name": "Squat", "sets": 5, "reps": 5, "weight_kg": 120.0}
        ]

        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Heavy Leg Day",
            workout_type="strength",
            duration_minutes=60,
            strength_exercises=exercises
        )

        assert result["strength_exercises"][0]["volume"] == 3000.0  # 4 * 5 * 150
        assert result["strength_exercises"][1]["volume"] == 3000.0  # 5 * 5 * 120

    def test_empty_query_results(self, gym_service, sample_user, fixed_datetime):
        """Test querying with no matching results."""
        gym_service.log_workout(
            user_id=sample_user.id,
            name="Short Workout",
            workout_type="cardio",
            duration_minutes=10,
            timestamp=fixed_datetime
        )

        # Query for long workouts that don't exist
        results = gym_service.query_workouts(
            user_id=sample_user.id,
            min_duration=60,
            start_date=fixed_datetime,
            end_date=fixed_datetime + timedelta(days=1)
        )

        assert len(results) == 0

    def test_cardio_with_distance(self, gym_service, sample_user):
        """Test cardio workout with distance tracking."""
        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Marathon Training",
            workout_type="cardio",
            duration_minutes=120,
            distance_km=21.1,
            calories_burned=2000.0,
            intensity="High"
        )

        assert result["distance_km"] == 21.1
        assert result["calories_burned"] == 2000.0

    def test_workout_without_optional_fields(self, gym_service, sample_user):
        """Test logging minimal workout."""
        result = gym_service.log_workout(
            user_id=sample_user.id,
            name="Quick Session",
            workout_type="flexibility",
            duration_minutes=15
        )

        assert result["name"] == "Quick Session"
        assert result["type"] == "flexibility"
        assert result["duration_minutes"] == 15
        assert result["calories_burned"] is None
        assert result["distance_km"] is None
        assert result["notes"] is None
