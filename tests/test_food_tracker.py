"""Unit tests for Food Tracker Service."""

import pytest
from datetime import datetime, timedelta
from src.modules.food_tracker.service import FoodTrackerService


class TestFoodTrackerService:
    """Test suite for FoodTrackerService."""

    @pytest.fixture
    def food_service(self, db_session):
        """Create a food tracker service instance."""
        return FoodTrackerService(db_session)

    def test_log_food_success(self, food_service, sample_user):
        """Test logging food entry successfully."""
        result = food_service.log_food(
            user_id=sample_user.id,
            calories=500.0,
            meal_name="Breakfast",
            meal_type="breakfast"
        )
        
        assert result is not None
        assert result["user_id"] == sample_user.id
        assert result["calories"] == 500.0
        assert result["meal_name"] == "Breakfast"
        assert result["meal_type"] == "breakfast"

    def test_log_food_minimal(self, food_service, sample_user):
        """Test logging food with minimal information."""
        result = food_service.log_food(
            user_id=sample_user.id,
            calories=300.0
        )
        
        assert result["calories"] == 300.0
        assert "timestamp" in result

    def test_log_food_custom_timestamp(self, food_service, sample_user, fixed_datetime):
        """Test logging food with custom timestamp."""
        result = food_service.log_food(
            user_id=sample_user.id,
            calories=400.0,
            timestamp=fixed_datetime
        )
        
        assert result["calories"] == 400.0
        assert result["timestamp"] == fixed_datetime.isoformat()

    def test_get_daily_summary(self, food_service, sample_user, fixed_datetime):
        """Test getting daily food summary."""
        # Log multiple food entries
        food_service.log_food(sample_user.id, 500.0, fixed_datetime, "Breakfast")
        food_service.log_food(sample_user.id, 700.0, fixed_datetime, "Lunch")
        food_service.log_food(sample_user.id, 600.0, fixed_datetime, "Dinner")
        
        summary = food_service.get_daily_summary(sample_user.id, fixed_datetime)
        
        assert summary["total_calories"] == 1800.0
        assert summary["entry_count"] == 3

    def test_get_weekly_summary(self, food_service, sample_user, fixed_datetime):
        """Test getting weekly food summary."""
        # Log entries across multiple days
        for i in range(7):
            date = fixed_datetime - timedelta(days=i)
            food_service.log_food(sample_user.id, 2000.0, date)
        
        summary = food_service.get_weekly_summary(sample_user.id, fixed_datetime)
        
        assert summary["total_calories"] == 14000.0
        assert summary["entry_count"] == 7
        assert summary["average_daily_calories"] == 2000.0

    def test_get_by_meal_type(self, food_service, sample_user, fixed_datetime):
        """Test filtering entries by meal type."""
        food_service.log_food(sample_user.id, 500.0, fixed_datetime, "Eggs", "breakfast")
        food_service.log_food(sample_user.id, 700.0, fixed_datetime, "Salad", "lunch")
        food_service.log_food(sample_user.id, 400.0, fixed_datetime, "Smoothie", "snack")
        
        breakfast_entries = food_service.get_entries_by_meal_type(
            sample_user.id,
            "breakfast",
            fixed_datetime
        )
        
        assert len(breakfast_entries) == 1
        assert breakfast_entries[0]["meal_type"] == "breakfast"

    def test_update_entry(self, food_service, sample_user):
        """Test updating a food entry."""
        entry = food_service.log_food(sample_user.id, 500.0, meal_name="Breakfast")
        entry_id = entry["id"]
        
        updated = food_service.update_entry(
            entry_id=entry_id,
            calories=600.0,
            meal_name="Big Breakfast"
        )
        
        assert updated["calories"] == 600.0
        assert updated["meal_name"] == "Big Breakfast"

    def test_delete_entry(self, food_service, sample_user):
        """Test deleting a food entry."""
        entry = food_service.log_food(sample_user.id, 500.0)
        entry_id = entry["id"]
        
        result = food_service.delete_entry(entry_id)
        
        assert result is True

    def test_calories_by_meal_type_summary(self, food_service, sample_user, fixed_datetime):
        """Test getting calories breakdown by meal type."""
        food_service.log_food(sample_user.id, 500.0, fixed_datetime, "Eggs", "breakfast")
        food_service.log_food(sample_user.id, 700.0, fixed_datetime, "Salad", "lunch")
        food_service.log_food(sample_user.id, 600.0, fixed_datetime, "Chicken", "dinner")
        food_service.log_food(sample_user.id, 200.0, fixed_datetime, "Snack", "snack")
        
        breakdown = food_service.get_calories_by_meal_type(sample_user.id, fixed_datetime)
        
        assert "breakfast" in breakdown
        assert "lunch" in breakdown
        assert "dinner" in breakdown
        assert "snack" in breakdown
        assert breakdown["breakfast"] == 500.0
