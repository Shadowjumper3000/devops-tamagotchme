"""Unit tests for Dashboard Service - Main Business Logic Orchestration."""

import pytest
from datetime import datetime, timedelta
from src.core.dashboard_service import DashboardService


class TestDashboardService:
    """Test suite for DashboardService."""

    @pytest.fixture
    def dashboard_service(self, db_session):
        """Create a dashboard service instance."""
        return DashboardService(db_session)

    def test_get_dashboard_data_complete(self, dashboard_service, sample_user, fixed_datetime):
        """Test getting complete dashboard data."""
        # Log some activities
        dashboard_service.water_service.log_water(sample_user.id, 500.0, fixed_datetime)
        dashboard_service.food_service.log_food(sample_user.id, 600.0, fixed_datetime)
        exercises = [{"exercise": "Push-ups", "reps": 20, "weight": 0}]
        dashboard_service.gym_service.log_hiit_workout(sample_user.id, exercises, fixed_datetime)
        
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        assert "user" in result
        assert "date" in result
        assert "pet_health" in result
        assert "today_summary" in result
        assert "goals" in result
        assert "progress" in result
        
        assert result["user"]["id"] == sample_user.id
        assert result["today_summary"]["water"]["total_ml"] == 500.0
        assert result["today_summary"]["food"]["total_calories"] == 600.0
        assert result["today_summary"]["gym"]["workout_count"] == 1

    def test_get_dashboard_data_no_activity(self, dashboard_service, sample_user, fixed_datetime):
        """Test dashboard with no tracked activity."""
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        assert result["today_summary"]["water"]["total_ml"] == 0
        assert result["today_summary"]["food"]["total_calories"] == 0
        assert result["today_summary"]["gym"]["workout_count"] == 0
        assert result["pet_health"]["overall_health"] < 50  # Poor health with no activity

    def test_dashboard_pet_health_calculation(self, dashboard_service, sample_user, fixed_datetime):
        """Test that pet health is properly calculated in dashboard."""
        # Perfect day
        dashboard_service.water_service.log_water(sample_user.id, 2000.0, fixed_datetime)
        dashboard_service.food_service.log_food(sample_user.id, 2000.0, fixed_datetime)
        exercises = [{"exercise": "Running", "reps": 1, "weight": 0}]
        dashboard_service.gym_service.log_hiit_workout(sample_user.id, exercises, fixed_datetime)
        dashboard_service.gym_service.log_cardio_workout(sample_user.id, "running", 30, 5.0, fixed_datetime)
        
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        assert result["pet_health"]["overall_health"] >= 80
        assert "status" in result["pet_health"]
        assert "message" in result["pet_health"]

    def test_dashboard_progress_calculation(self, dashboard_service, sample_user, fixed_datetime):
        """Test progress calculation against goals."""
        # 50% of water goal, 75% of calorie goal
        dashboard_service.water_service.log_water(sample_user.id, 1000.0, fixed_datetime)
        dashboard_service.food_service.log_food(sample_user.id, 1500.0, fixed_datetime)
        
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        progress = result["progress"]
        assert "water_progress" in progress
        assert "food_progress" in progress
        assert 45 <= progress["water_progress"] <= 55  # ~50%
        assert 70 <= progress["food_progress"] <= 80  # ~75%

    def test_get_weekly_trends(self, dashboard_service, sample_user, fixed_datetime):
        """Test getting weekly trends."""
        # Log activities across multiple days
        for i in range(7):
            date = fixed_datetime - timedelta(days=i)
            dashboard_service.water_service.log_water(sample_user.id, 2000.0, date)
            dashboard_service.food_service.log_food(sample_user.id, 2000.0, date)
        
        result = dashboard_service.get_weekly_trends(sample_user.id, fixed_datetime)
        
        assert "water_trend" in result
        assert "food_trend" in result
        assert "exercise_trend" in result
        assert result["water_trend"]["total"] == 14000.0
        assert result["food_trend"]["total"] == 14000.0

    def test_dashboard_with_user_not_found(self, dashboard_service, fixed_datetime):
        """Test dashboard with non-existent user."""
        with pytest.raises(ValueError, match="User .* not found"):
            dashboard_service.get_dashboard_data(99999, fixed_datetime)

    def test_dashboard_default_date(self, dashboard_service, sample_user):
        """Test dashboard with default date (today)."""
        result = dashboard_service.get_dashboard_data(sample_user.id)
        
        assert "date" in result
        # Should use today's date
        assert result["date"] == datetime.now().date().isoformat()

    def test_dashboard_goals_included(self, dashboard_service, sample_user, fixed_datetime):
        """Test that user goals are included in dashboard."""
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        goals = result["goals"]
        assert goals["daily_water_ml"] == sample_user.daily_water_goal
        assert goals["daily_calories"] == sample_user.daily_calorie_goal
        assert goals["weekly_exercise"] == sample_user.weekly_exercise_goal

    def test_dashboard_multiple_entries_same_day(self, dashboard_service, sample_user, fixed_datetime):
        """Test dashboard with multiple entries on same day."""
        # Log multiple entries
        dashboard_service.water_service.log_water(sample_user.id, 500.0, fixed_datetime)
        dashboard_service.water_service.log_water(sample_user.id, 300.0, fixed_datetime)
        dashboard_service.water_service.log_water(sample_user.id, 200.0, fixed_datetime)
        
        dashboard_service.food_service.log_food(sample_user.id, 400.0, fixed_datetime)
        dashboard_service.food_service.log_food(sample_user.id, 600.0, fixed_datetime)
        
        result = dashboard_service.get_dashboard_data(sample_user.id, fixed_datetime)
        
        assert result["today_summary"]["water"]["total_ml"] == 1000.0
        assert result["today_summary"]["water"]["entry_count"] == 3
        assert result["today_summary"]["food"]["total_calories"] == 1000.0
        assert result["today_summary"]["food"]["entry_count"] == 2

    def test_weekly_summary_consistency(self, dashboard_service, sample_user, fixed_datetime):
        """Test that weekly trends are consistent with daily data."""
        # Log same amount for 7 days
        daily_water = 2000.0
        for i in range(7):
            date = fixed_datetime - timedelta(days=i)
            dashboard_service.water_service.log_water(sample_user.id, daily_water, date)
        
        result = dashboard_service.get_weekly_trends(sample_user.id, fixed_datetime)
        
        assert result["water_trend"]["total"] == daily_water * 7
        assert result["water_trend"]["average"] == daily_water
