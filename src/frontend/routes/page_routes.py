"""Page routes for main application pages (home, water, food, gym)."""

import logging
from flask import Blueprint, render_template, session
from datetime import datetime
from ..utils import login_required

logger = logging.getLogger(__name__)


def create_page_routes(coordinator):
    """Create and configure page routes."""
    pages = Blueprint("pages", __name__)

    @pages.route("/home")
    @login_required
    def home():
        """Home page with Tamagotchi."""
        user_id = session.get("user_id")

        try:
            # Get dashboard data from coordinator
            dashboard_data = coordinator.get_daily_summary(user_id)
            pet_health = coordinator.get_pet_health(user_id)

            tamagotchi = {
                "name": "TamagotchMe",
                "health": pet_health.get("overall_health", 50),
                "status": pet_health.get("status", "okay"),
            }

            stats = {
                "water_today": dashboard_data.get("water", {}).get("total_ml", 0),
                "calories_today": dashboard_data.get("food", {}).get(
                    "total_calories", 0
                ),
                "workout_minutes": dashboard_data.get("gym", {}).get(
                    "total_cardio_minutes", 0
                ),
            }
        except Exception as e:
            logger.error("Failed to get dashboard data: %s", e)
            tamagotchi = {"name": "TamagotchMe", "health": 50, "status": "okay"}
            stats = {"water_today": 0, "calories_today": 0, "workout_minutes": 0}

        return render_template(
            "home.html",
            username=session.get("email"),
            tamagotchi=tamagotchi,
            stats=stats,
        )

    @pages.route("/water")
    @login_required
    def water_page():
        """Water tracker page."""
        user_id = session.get("user_id")

        try:
            # Get water data from coordinator
            water_service = coordinator.get_service("water_tracker")
            user = coordinator.get_user(user_id)

            daily_summary = water_service.get_daily_summary(user_id, datetime.now())
            weekly_summary = water_service.get_weekly_summary(user_id, datetime.now())

            daily_goal = user.get("daily_water_goal", 2000)
            today_total = daily_summary.get("total_ml", 0)

            analytics = {
                "today_total": today_total,
                "today_percentage": int(
                    (today_total / daily_goal * 100) if daily_goal > 0 else 0
                ),
                "daily_goal": daily_goal,
                "weekly_avg": weekly_summary.get("average_daily_ml", 0),
                "weekly_total": weekly_summary.get("total_ml", 0),
                "streak": 0,  # TODO: Implement streak calculation
            }

            # Get recent entries
            history = (
                water_service.get_entries_by_date_range(
                    user_id,
                    datetime.now().replace(hour=0, minute=0, second=0),
                    datetime.now(),
                )
                or []
            )
        except Exception as e:
            logger.error("Failed to get water data: %s", e)
            analytics = {
                "today_total": 0,
                "today_percentage": 0,
                "daily_goal": 2000,
                "weekly_avg": 0,
                "weekly_total": 0,
                "streak": 0,
            }
            history = []

        return render_template("water.html", analytics=analytics, history=history)

    @pages.route("/food")
    @login_required
    def food_page():
        """Food tracker page."""
        user_id = session.get("user_id")

        try:
            # Get food data from coordinator
            food_service = coordinator.get_service("food_tracker")
            user = coordinator.get_user(user_id)

            daily_summary = food_service.get_daily_summary(user_id, datetime.now())

            calorie_goal = user.get("daily_calorie_goal", 2000)
            today_calories = daily_summary.get("total_calories", 0)

            analytics = {
                "today_calories": today_calories,
                "calorie_percentage": int(
                    (today_calories / calorie_goal * 100) if calorie_goal > 0 else 0
                ),
                "calorie_goal": calorie_goal,
                "today_protein": daily_summary.get("total_protein", 0),
                "protein_percentage": 0,  # Can be calculated if protein goal is added
                "today_carbs": daily_summary.get("total_carbs", 0),
                "carbs_percentage": 0,
                "today_fats": daily_summary.get("total_fats", 0),
                "fats_percentage": 0,
            }

            # Get today's meals
            meals = (
                food_service.get_entries_by_date_range(
                    user_id,
                    datetime.now().replace(hour=0, minute=0, second=0),
                    datetime.now(),
                )
                or []
            )
        except Exception as e:
            logger.error("Failed to get food data: %s", e)
            analytics = {
                "today_calories": 0,
                "calorie_percentage": 0,
                "calorie_goal": 2000,
                "today_protein": 0,
                "protein_percentage": 0,
                "today_carbs": 0,
                "carbs_percentage": 0,
                "today_fats": 0,
                "fats_percentage": 0,
            }
            meals = []

        return render_template("food.html", analytics=analytics, meals=meals)

    @pages.route("/gym")
    @login_required
    def gym_page():
        """Gym tracker page."""
        user_id = session.get("user_id")

        try:
            # Get gym data from coordinator
            gym_service = coordinator.get_service("gym_tracker")

            daily_summary = gym_service.get_daily_summary(user_id, datetime.now())
            weekly_summary = gym_service.get_weekly_summary(user_id, datetime.now())

            today_minutes = daily_summary.get("total_cardio_minutes", 0)
            daily_goal = 60  # Default goal

            analytics = {
                "today_minutes": today_minutes,
                "goal_percentage": int(
                    (today_minutes / daily_goal * 100) if daily_goal > 0 else 0
                ),
                "daily_goal": daily_goal,
                "weekly_minutes": weekly_summary.get("total_cardio_minutes", 0),
                "weekly_workouts": weekly_summary.get("workout_count", 0),
                "calories_burned": daily_summary.get("estimated_calories", 0),
                "streak": 0,  # TODO: Implement streak
            }

            # Get today's workouts
            workouts = (
                gym_service.get_entries_by_date_range(
                    user_id,
                    datetime.now().replace(hour=0, minute=0, second=0),
                    datetime.now(),
                )
                or []
            )
        except Exception as e:
            logger.error("Failed to get gym data: %s", e)
            analytics = {
                "today_minutes": 0,
                "goal_percentage": 0,
                "daily_goal": 60,
                "weekly_minutes": 0,
                "weekly_workouts": 0,
                "calories_burned": 0,
                "streak": 0,
            }
            workouts = []

        return render_template("gym.html", analytics=analytics, workouts=workouts)

    return pages
