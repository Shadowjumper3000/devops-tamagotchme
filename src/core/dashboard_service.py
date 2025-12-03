"""Dashboard service for aggregating tracker data and providing pet health insights."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from .health_calculator import PetHealthCalculator
from ..modules.auth.repository import UserRepository
from ..modules.water_tracker.service import WaterTrackerService
from ..modules.food_tracker.service import FoodTrackerService
from ..modules.gym_tracker.service import GymTrackerService

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Dashboard service that provides comprehensive health insights.
    
    This service is the main orchestration layer that:
    1. Aggregates data from all tracker modules
    2. Retrieves user goals and preferences
    3. Calculates pet health using the health calculator
    4. Provides weekly trends and analytics
    """

    def __init__(self, db_session: Session):
        """
        Initialize dashboard service with all necessary services.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session
        self.user_repository = UserRepository(db_session)
        self.water_service = WaterTrackerService(db_session)
        self.food_service = FoodTrackerService(db_session)
        self.gym_service = GymTrackerService(db_session)
        self.health_calculator = PetHealthCalculator()

    def get_dashboard_data(
        self,
        user_id: int,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data for a user.
        
        Args:
            user_id: User's ID
            date: Date to get data for (defaults to today)
            
        Returns:
            Complete dashboard data including pet health and all tracker summaries
        """
        try:
            if date is None:
                date = datetime.now()
            
            # Get user and goals
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            user_goals = {
                "daily_water_ml": user.daily_water_goal,
                "daily_calories": user.daily_calorie_goal,
                "weekly_exercise": user.weekly_exercise_goal
            }
            
            # Get daily summaries from all trackers
            water_summary = self.water_service.get_daily_summary(user_id, date)
            food_summary = self.food_service.get_daily_summary(user_id, date)
            gym_summary = self.gym_service.get_daily_summary(user_id, date)
            
            # Calculate pet health
            pet_health = self.health_calculator.calculate_pet_health(
                water_summary=water_summary,
                food_summary=food_summary,
                gym_summary=gym_summary,
                user_goals=user_goals
            )
            
            # Compile dashboard data
            dashboard = {
                "user": user.to_dict(),
                "date": date.date().isoformat(),
                "pet_health": pet_health,
                "today_summary": {
                    "water": water_summary,
                    "food": food_summary,
                    "gym": gym_summary
                },
                "goals": user_goals,
                "progress": self._calculate_goal_progress(
                    water_summary,
                    food_summary,
                    gym_summary,
                    user_goals
                )
            }
            
            logger.info(f"Dashboard data retrieved for user {user_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise

    def get_weekly_dashboard(
        self,
        user_id: int,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get weekly dashboard with trends and analytics.
        
        Args:
            user_id: User's ID
            start_date: Start of week (defaults to 7 days ago)
            
        Returns:
            Weekly dashboard data with trends
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=7)
            
            # Get user and goals
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            user_goals = {
                "daily_water_ml": user.daily_water_goal,
                "daily_calories": user.daily_calorie_goal,
                "weekly_exercise": user.weekly_exercise_goal
            }
            
            # Get weekly summaries
            water_summary = self.water_service.get_weekly_summary(user_id, start_date)
            food_summary = self.food_service.get_weekly_summary(user_id, start_date)
            gym_summary = self.gym_service.get_weekly_summary(user_id, start_date)
            
            # Calculate daily health scores for the week
            daily_health_scores = []
            current_date = start_date
            end_date = start_date + timedelta(days=7)
            
            while current_date < end_date:
                daily_water = self.water_service.get_daily_summary(user_id, current_date)
                daily_food = self.food_service.get_daily_summary(user_id, current_date)
                daily_gym = self.gym_service.get_daily_summary(user_id, current_date)
                
                daily_health = self.health_calculator.calculate_pet_health(
                    water_summary=daily_water,
                    food_summary=daily_food,
                    gym_summary=daily_gym,
                    user_goals=user_goals
                )
                
                daily_health_scores.append(daily_health["overall_health"])
                current_date += timedelta(days=1)
            
            # Calculate weekly trend
            weekly_trend = self.health_calculator.calculate_weekly_trend(daily_health_scores)
            
            # Compile weekly dashboard
            weekly_dashboard = {
                "user": user.to_dict(),
                "period": {
                    "start_date": start_date.date().isoformat(),
                    "end_date": end_date.date().isoformat()
                },
                "weekly_summary": {
                    "water": water_summary,
                    "food": food_summary,
                    "gym": gym_summary
                },
                "health_trend": weekly_trend,
                "daily_scores": daily_health_scores,
                "goals": user_goals,
                "achievements": self._generate_weekly_achievements(
                    water_summary,
                    food_summary,
                    gym_summary,
                    user_goals
                )
            }
            
            logger.info(f"Weekly dashboard data retrieved for user {user_id}")
            return weekly_dashboard
            
        except Exception as e:
            logger.error(f"Error getting weekly dashboard: {e}")
            raise

    def _calculate_goal_progress(
        self,
        water_summary: Dict[str, Any],
        food_summary: Dict[str, Any],
        gym_summary: Dict[str, Any],
        user_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate progress towards daily goals.
        
        Args:
            water_summary: Daily water summary
            food_summary: Daily food summary
            gym_summary: Daily gym summary
            user_goals: User's goals
            
        Returns:
            Progress percentages for each goal
        """
        water_progress = (
            (water_summary.get("total_ml", 0) / user_goals["daily_water_ml"]) * 100
            if user_goals["daily_water_ml"] > 0 else 0
        )
        
        # For calories, 90-110% is optimal
        calorie_actual = food_summary.get("total_calories", 0)
        calorie_goal = user_goals["daily_calories"]
        if calorie_goal > 0:
            calorie_percentage = (calorie_actual / calorie_goal) * 100
            # Calculate how close to optimal range (90-110%)
            if 90 <= calorie_percentage <= 110:
                calorie_progress = 100
            elif calorie_percentage < 90:
                calorie_progress = (calorie_percentage / 90) * 100
            else:
                # Over 110%, decrease progress
                excess = calorie_percentage - 110
                calorie_progress = max(0, 100 - (excess / 2))
        else:
            calorie_progress = 0
        
        # Exercise: 1 workout = 100% for daily goal
        exercise_progress = min(100, gym_summary.get("workout_count", 0) * 100)
        
        return {
            "water": {
                "current": water_summary.get("total_ml", 0),
                "goal": user_goals["daily_water_ml"],
                "percentage": min(100, round(water_progress, 1)),
                "achieved": water_progress >= 100
            },
            "calories": {
                "current": food_summary.get("total_calories", 0),
                "goal": user_goals["daily_calories"],
                "percentage": round(calorie_progress, 1),
                "achieved": 90 <= (calorie_actual / calorie_goal * 100 if calorie_goal > 0 else 0) <= 110
            },
            "exercise": {
                "current": gym_summary.get("workout_count", 0),
                "goal": 1,  # Daily goal is 1 workout
                "percentage": round(exercise_progress, 1),
                "achieved": gym_summary.get("workout_count", 0) >= 1
            }
        }

    def _generate_weekly_achievements(
        self,
        water_summary: Dict[str, Any],
        food_summary: Dict[str, Any],
        gym_summary: Dict[str, Any],
        user_goals: Dict[str, Any]
    ) -> list:
        """
        Generate achievement badges for the week.
        
        Args:
            water_summary: Weekly water summary
            food_summary: Weekly food summary
            gym_summary: Weekly gym summary
            user_goals: User's goals
            
        Returns:
            List of achievements earned
        """
        achievements = []
        
        # Water achievements
        weekly_water_goal = user_goals["daily_water_ml"] * 7
        if water_summary.get("total_ml", 0) >= weekly_water_goal:
            achievements.append({
                "name": "Hydration Hero",
                "description": "Met your water goal every day this week!",
                "icon": "💧"
            })
        
        # Exercise achievements
        if gym_summary.get("total_workouts", 0) >= user_goals["weekly_exercise"]:
            achievements.append({
                "name": "Fitness Champion",
                "description": f"Completed {gym_summary.get('total_workouts', 0)} workouts this week!",
                "icon": "💪"
            })
        
        if gym_summary.get("active_days", 0) == 7:
            achievements.append({
                "name": "Perfect Week",
                "description": "Worked out every single day!",
                "icon": "🌟"
            })
        
        # Consistency achievement
        if (gym_summary.get("total_workouts", 0) >= user_goals["weekly_exercise"] and
            water_summary.get("total_ml", 0) >= weekly_water_goal * 0.9):
            achievements.append({
                "name": "Consistency King/Queen",
                "description": "Maintained great habits all week long!",
                "icon": "👑"
            })
        
        return achievements

    def get_status(self) -> Dict[str, Any]:
        """
        Get dashboard service status.
        
        Returns:
            Service status
        """
        return {
            "service": "DashboardService",
            "status": "operational",
            "components": {
                "water_tracker": self.water_service.get_status(),
                "food_tracker": self.food_service.get_status(),
                "gym_tracker": self.gym_service.get_status()
            }
        }
