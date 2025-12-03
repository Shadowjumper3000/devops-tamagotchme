"""Unit tests for Health Calculator - Core Business Logic."""

import pytest
from src.core.health_calculator import PetHealthCalculator, HealthStatus


class TestPetHealthCalculator:
    """Test suite for PetHealthCalculator."""

    @pytest.fixture
    def calculator(self):
        """Create a health calculator instance."""
        return PetHealthCalculator()

    @pytest.fixture
    def perfect_goals(self):
        """User goals for perfect health."""
        return {
            "daily_water_ml": 2000,
            "daily_calories": 2000,
            "weekly_exercise": 3
        }

    def test_perfect_health(self, calculator, perfect_goals):
        """Test health calculation with perfect adherence to goals."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 2000}
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["overall_health"] >= 90
        assert result["status"] == HealthStatus.THRIVING
        assert result["water_score"] >= 90
        assert result["food_score"] >= 90
        assert result["exercise_score"] >= 90

    def test_no_activity(self, calculator, perfect_goals):
        """Test health with no tracked activity."""
        water_summary = {"total_ml": 0}
        food_summary = {"total_calories": 0}
        gym_summary = {"workout_count": 0, "total_cardio_minutes": 0}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["overall_health"] <= 30
        assert result["status"] in [HealthStatus.CRITICAL, HealthStatus.NEEDS_ATTENTION]

    def test_water_only_tracking(self, calculator, perfect_goals):
        """Test health with only water tracking."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 0}
        gym_summary = {"workout_count": 0, "total_cardio_minutes": 0}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        # Water is 30% of total score, so max would be 30
        assert result["water_score"] >= 90
        assert result["overall_health"] < 50  # Should be okay or needs attention

    def test_excessive_calories(self, calculator, perfect_goals):
        """Test health with excessive calorie intake."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 4000}  # 2x goal
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["food_score"] < 70  # Penalized for excess
        assert result["overall_health"] < 90

    def test_insufficient_calories(self, calculator, perfect_goals):
        """Test health with insufficient calorie intake."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 800}  # Very low
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["food_score"] < 70  # Penalized for being too low

    def test_excellent_exercise(self, calculator, perfect_goals):
        """Test health with excellent exercise routine."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 2000}
        gym_summary = {"workout_count": 2, "total_cardio_minutes": 60}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["exercise_score"] >= 95
        assert result["overall_health"] >= 90

    def test_weight_distribution(self, calculator, perfect_goals):
        """Test that weights are properly distributed (30-30-40)."""
        # Perfect in one area, zero in others
        water_perfect = {"total_ml": 2000}
        food_zero = {"total_calories": 0}
        gym_zero = {"workout_count": 0, "total_cardio_minutes": 0}
        
        result = calculator.calculate_pet_health(
            water_perfect,
            food_zero,
            gym_zero,
            perfect_goals
        )
        
        # Water contributes 30%, so perfect water = ~27-30 points
        assert 20 <= result["overall_health"] <= 35

    def test_status_messages(self, calculator, perfect_goals):
        """Test that status messages are included."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 2000}
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert "message" in result
        assert "🌟" in result["message"] or "😊" in result["message"]

    def test_dehydration_penalty(self, calculator, perfect_goals):
        """Test severe penalty for dehydration."""
        water_summary = {"total_ml": 200}  # Only 10% of goal
        food_summary = {"total_calories": 2000}
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert result["water_score"] < 30
        assert result["overall_health"] < 70

    def test_healthy_status_threshold(self, calculator, perfect_goals):
        """Test healthy status threshold (70-90)."""
        water_summary = {"total_ml": 1800}  # Slightly under goal
        food_summary = {"total_calories": 1900}
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 25}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        # Should be in healthy range
        assert 60 <= result["overall_health"] <= 90
        assert result["status"] in [HealthStatus.HEALTHY, HealthStatus.OKAY]

    def test_component_scores_included(self, calculator, perfect_goals):
        """Test that all component scores are included in result."""
        water_summary = {"total_ml": 2000}
        food_summary = {"total_calories": 2000}
        gym_summary = {"workout_count": 1, "total_cardio_minutes": 30}
        
        result = calculator.calculate_pet_health(
            water_summary,
            food_summary,
            gym_summary,
            perfect_goals
        )
        
        assert "water_score" in result
        assert "food_score" in result
        assert "exercise_score" in result
        assert "overall_health" in result
        assert "status" in result
        assert "message" in result
