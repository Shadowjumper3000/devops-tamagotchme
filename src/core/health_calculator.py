"""Pet Health Calculator - Core business logic for calculating pet health based on user tracking data."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class HealthStatus:
    """Health status constants."""
    CRITICAL = "critical"
    NEEDS_ATTENTION = "needs_attention"
    OKAY = "okay"
    HEALTHY = "healthy"
    THRIVING = "thriving"


class PetHealthCalculator:
    """
    Calculates pet health score based on water, food, and exercise tracking.
    
    The pet health is a gamification layer that encourages healthy habits.
    Health is calculated on a 0-100 scale with weighted contributions from:
    - Water intake: 30%
    - Calorie intake: 30%
    - Exercise: 40%
    """

    # Weight factors for each health component
    WATER_WEIGHT = 0.30
    FOOD_WEIGHT = 0.30
    EXERCISE_WEIGHT = 0.40

    # Health status thresholds
    STATUS_THRESHOLDS = {
        90: HealthStatus.THRIVING,
        70: HealthStatus.HEALTHY,
        50: HealthStatus.OKAY,
        30: HealthStatus.NEEDS_ATTENTION,
        0: HealthStatus.CRITICAL
    }

    # Status messages
    STATUS_MESSAGES = {
        HealthStatus.THRIVING: "🌟 Your pet is thriving! Keep up the excellent work!",
        HealthStatus.HEALTHY: "😊 Your pet is healthy and happy!",
        HealthStatus.OKAY: "😐 Your pet is doing okay, but could use more attention.",
        HealthStatus.NEEDS_ATTENTION: "😟 Your pet needs attention! Try to improve your habits.",
        HealthStatus.CRITICAL: "😰 Critical! Your pet really needs your care right now!"
    }

    def __init__(self):
        """Initialize the health calculator."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_pet_health(
        self,
        water_summary: Dict[str, Any],
        food_summary: Dict[str, Any],
        gym_summary: Dict[str, Any],
        user_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate overall pet health based on daily tracking data.
        
        Args:
            water_summary: Daily water summary with total_ml
            food_summary: Daily food summary with total_calories
            gym_summary: Daily gym summary with workout_count
            user_goals: User's daily goals (water_ml, calories, exercise_frequency)
            
        Returns:
            Dictionary with health scores and status
        """
        try:
            # Calculate individual component scores
            water_score = self._calculate_water_score(
                water_summary.get("total_ml", 0),
                user_goals.get("daily_water_ml", 2000)
            )
            
            food_score = self._calculate_food_score(
                food_summary.get("total_calories", 0),
                user_goals.get("daily_calories", 2000)
            )
            
            exercise_score = self._calculate_exercise_score(
                gym_summary.get("workout_count", 0),
                gym_summary.get("total_cardio_minutes", 0)
            )
            
            # Calculate weighted overall health
            overall_health = (
                water_score * self.WATER_WEIGHT +
                food_score * self.FOOD_WEIGHT +
                exercise_score * self.EXERCISE_WEIGHT
            )
            
            # Determine status
            status = self._get_health_status(overall_health)
            message = self.STATUS_MESSAGES[status]
            
            return {
                "overall_health": round(overall_health, 2),
                "status": status,
                "message": message,
                "components": {
                    "water": {
                        "score": round(water_score, 2),
                        "weight": self.WATER_WEIGHT,
                        "contribution": round(water_score * self.WATER_WEIGHT, 2)
                    },
                    "food": {
                        "score": round(food_score, 2),
                        "weight": self.FOOD_WEIGHT,
                        "contribution": round(food_score * self.FOOD_WEIGHT, 2)
                    },
                    "exercise": {
                        "score": round(exercise_score, 2),
                        "weight": self.EXERCISE_WEIGHT,
                        "contribution": round(exercise_score * self.EXERCISE_WEIGHT, 2)
                    }
                },
                "recommendations": self._generate_recommendations(
                    water_score, food_score, exercise_score
                )
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating pet health: {e}")
            return self._get_default_health()

    def _calculate_water_score(self, actual_ml: float, goal_ml: float) -> float:
        """
        Calculate water intake score (0-100).
        
        Scoring logic:
        - 100%+ of goal: 100 points
        - 75-99% of goal: 70-99 points (linear)
        - 50-74% of goal: 40-69 points (linear)
        - <50% of goal: 0-39 points (linear)
        
        Args:
            actual_ml: Actual water consumed
            goal_ml: Daily water goal
            
        Returns:
            Score from 0-100
        """
        if goal_ml == 0:
            return 0
        
        percentage = (actual_ml / goal_ml) * 100
        
        if percentage >= 100:
            return 100
        elif percentage >= 75:
            # Linear scale: 75% = 70 points, 99% = 99 points
            return 70 + (percentage - 75) * (29 / 24)
        elif percentage >= 50:
            # Linear scale: 50% = 40 points, 74% = 69 points
            return 40 + (percentage - 50) * (29 / 24)
        else:
            # Linear scale: 0% = 0 points, 49% = 39 points
            return percentage * (39 / 49) if percentage > 0 else 0

    def _calculate_food_score(self, actual_calories: float, goal_calories: float) -> float:
        """
        Calculate food/calorie intake score (0-100).
        
        Scoring logic (considers both under and over-eating):
        - 90-110% of goal: 100 points (optimal range)
        - 75-89% or 111-125% of goal: 70-99 points
        - 50-74% or 126-150% of goal: 40-69 points
        - <50% or >150% of goal: 0-39 points
        
        Args:
            actual_calories: Actual calories consumed
            goal_calories: Daily calorie goal
            
        Returns:
            Score from 0-100
        """
        if goal_calories == 0:
            return 0
        
        percentage = (actual_calories / goal_calories) * 100
        
        # Optimal range: 90-110%
        if 90 <= percentage <= 110:
            return 100
        
        # Calculate distance from optimal range
        if percentage < 90:
            # Under-eating
            if percentage >= 75:
                return 70 + (percentage - 75) * (29 / 15)
            elif percentage >= 50:
                return 40 + (percentage - 50) * (29 / 25)
            else:
                return percentage * (39 / 50) if percentage > 0 else 0
        else:
            # Over-eating (percentage > 110)
            if percentage <= 125:
                return 99 - (percentage - 110) * (29 / 15)
            elif percentage <= 150:
                return 69 - (percentage - 125) * (29 / 25)
            else:
                # Significantly over goal
                excess = min(percentage - 150, 50)
                return max(0, 39 - (excess * 0.78))

    def _calculate_exercise_score(self, workout_count: int, cardio_minutes: float) -> float:
        """
        Calculate exercise score (0-100).
        
        Scoring logic:
        - 1+ workout: Base 50 points
        - 2+ workouts: 75 points
        - 3+ workouts: 100 points
        - Additional points for cardio duration (30+ min = bonus)
        
        Args:
            workout_count: Number of workouts today
            cardio_minutes: Total cardio minutes
            
        Returns:
            Score from 0-100
        """
        if workout_count == 0:
            return 0
        
        # Base score from workout count
        if workout_count >= 3:
            base_score = 100
        elif workout_count == 2:
            base_score = 75
        else:
            base_score = 50
        
        # Bonus for cardio duration (up to 20 additional points)
        cardio_bonus = 0
        if cardio_minutes >= 60:
            cardio_bonus = 20
        elif cardio_minutes >= 30:
            cardio_bonus = 10
        elif cardio_minutes >= 15:
            cardio_bonus = 5
        
        # Total score (capped at 100)
        total_score = min(100, base_score + cardio_bonus)
        
        return total_score

    def _get_health_status(self, health_score: float) -> str:
        """
        Determine health status based on score.
        
        Args:
            health_score: Overall health score (0-100)
            
        Returns:
            Health status string
        """
        for threshold, status in sorted(self.STATUS_THRESHOLDS.items(), reverse=True):
            if health_score >= threshold:
                return status
        return HealthStatus.CRITICAL

    def _generate_recommendations(
        self,
        water_score: float,
        food_score: float,
        exercise_score: float
    ) -> list:
        """
        Generate personalized recommendations based on scores.
        
        Args:
            water_score: Water component score
            food_score: Food component score
            exercise_score: Exercise component score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if water_score < 70:
            recommendations.append("💧 Drink more water to stay hydrated!")
        
        if food_score < 70:
            if food_score < 40:
                recommendations.append("🍽️ Try to eat more balanced meals and reach your calorie goal.")
            else:
                recommendations.append("🍎 Pay attention to your nutrition and meal balance.")
        
        if exercise_score < 70:
            if exercise_score == 0:
                recommendations.append("💪 Start with any exercise - even a 15-minute walk helps!")
            elif exercise_score < 50:
                recommendations.append("🏃 Add more workouts to your routine - aim for at least 30 minutes.")
            else:
                recommendations.append("🎯 You're close! Try to fit in one more workout today.")
        
        if not recommendations:
            recommendations.append("✨ You're doing great! Keep maintaining these healthy habits!")
        
        return recommendations

    def _get_default_health(self) -> Dict[str, Any]:
        """
        Get default health response in case of errors.
        
        Returns:
            Default health dictionary
        """
        return {
            "overall_health": 50,
            "status": HealthStatus.OKAY,
            "message": self.STATUS_MESSAGES[HealthStatus.OKAY],
            "components": {
                "water": {"score": 0, "weight": self.WATER_WEIGHT, "contribution": 0},
                "food": {"score": 0, "weight": self.FOOD_WEIGHT, "contribution": 0},
                "exercise": {"score": 0, "weight": self.EXERCISE_WEIGHT, "contribution": 0}
            },
            "recommendations": ["Unable to calculate health. Please try again."]
        }

    def calculate_weekly_trend(
        self,
        daily_health_scores: list
    ) -> Dict[str, Any]:
        """
        Calculate weekly health trend.
        
        Args:
            daily_health_scores: List of daily health scores (0-100)
            
        Returns:
            Trend analysis dictionary
        """
        if not daily_health_scores:
            return {"trend": "no_data", "average": 0, "consistency": 0}
        
        average = sum(daily_health_scores) / len(daily_health_scores)
        
        # Calculate trend (improving/declining/stable)
        if len(daily_health_scores) >= 3:
            recent_avg = sum(daily_health_scores[-3:]) / 3
            older_avg = sum(daily_health_scores[:-3]) / len(daily_health_scores[:-3])
            
            if recent_avg > older_avg + 5:
                trend = "improving"
            elif recent_avg < older_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Calculate consistency (how much variation)
        if len(daily_health_scores) > 1:
            variance = sum((x - average) ** 2 for x in daily_health_scores) / len(daily_health_scores)
            std_dev = variance ** 0.5
            consistency = max(0, 100 - std_dev)
        else:
            consistency = 100
        
        return {
            "trend": trend,
            "average": round(average, 2),
            "consistency": round(consistency, 2),
            "days_tracked": len(daily_health_scores)
        }
