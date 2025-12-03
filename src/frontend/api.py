"""REST API endpoints for the Tamagotchi Tracker."""

import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from .utils import require_auth

logger = logging.getLogger(__name__)


def create_api_blueprint(coordinator):
    """Create and configure the API blueprint."""
    api = Blueprint("api", __name__)

    @api.route("/water", methods=["GET", "POST"])
    def water():
        """Water tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        water_service = coordinator.get_service("water_tracker")
        if not water_service:
            return jsonify({"error": "Water service not available"}), 503

        if request.method == "POST":
            data = request.get_json()
            amount = data.get("amount")

            if not amount:
                return jsonify({"error": "Amount is required"}), 400

            try:
                entry = water_service.log_water(
                    user_id=user_id, amount_ml=float(amount), timestamp=datetime.now()
                )
                logger.info("Water logged: %sml for user %s", amount, user_id)

                return (
                    jsonify(
                        {
                            "success": True,
                            "message": "Water logged successfully",
                            "entry": entry,
                        }
                    ),
                    201,
                )
            except Exception as e:
                logger.error("Failed to log water: %s", e)
                return jsonify({"error": "Failed to log water"}), 500

        # GET request
        try:
            entries = water_service.get_entries_by_date_range(
                user_id,
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now(),
            )
            return jsonify({"entries": entries or []}), 200
        except Exception as e:
            logger.error("Failed to fetch water entries: %s", e)
            return jsonify({"entries": []}), 200

    @api.route("/water/<int:entry_id>", methods=["DELETE"])
    def delete_water(entry_id):
        """Delete water entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        water_service = coordinator.get_service("water_tracker")
        if not water_service:
            return jsonify({"error": "Water service not available"}), 503

        try:
            water_service.delete_entry(entry_id)
            logger.info("Water entry %s deleted for user %s", entry_id, user_id)

            return (
                jsonify({"success": True, "message": "Entry deleted successfully"}),
                200,
            )
        except Exception as e:
            logger.error("Failed to delete water entry: %s", e)
            return jsonify({"error": "Failed to delete entry"}), 500

    @api.route("/food", methods=["GET", "POST"])
    def food():
        """Food tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        food_service = coordinator.get_service("food_tracker")
        if not food_service:
            return jsonify({"error": "Food service not available"}), 503

        if request.method == "POST":
            data = request.get_json()
            meal_name = data.get("meal_name")
            calories = data.get("calories")
            meal_type = data.get("meal_type")

            if not calories:
                return jsonify({"error": "Calories is required"}), 400

            try:
                entry = food_service.log_food(
                    user_id=user_id,
                    calories=float(calories),
                    meal_name=meal_name,
                    meal_type=meal_type,
                    timestamp=datetime.now(),
                )
                logger.info(
                    "Meal logged: %s - %scal for user %s", meal_name, calories, user_id
                )

                return (
                    jsonify(
                        {
                            "success": True,
                            "message": "Meal logged successfully",
                            "entry": entry,
                        }
                    ),
                    201,
                )
            except Exception as e:
                logger.error("Failed to log meal: %s", e)
                return jsonify({"error": "Failed to log meal"}), 500

        # GET request
        try:
            meals = food_service.get_entries_by_date_range(
                user_id,
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now(),
            )
            return jsonify({"meals": meals or []}), 200
        except Exception as e:
            logger.error("Failed to fetch meals: %s", e)
            return jsonify({"meals": []}), 200

    @api.route("/food/<int:meal_id>", methods=["DELETE"])
    def delete_meal(meal_id):
        """Delete meal entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        food_service = coordinator.get_service("food_tracker")
        if not food_service:
            return jsonify({"error": "Food service not available"}), 503

        try:
            food_service.delete_entry(meal_id)
            logger.info("Meal %s deleted for user %s", meal_id, user_id)

            return (
                jsonify({"success": True, "message": "Meal deleted successfully"}),
                200,
            )
        except Exception as e:
            logger.error("Failed to delete meal: %s", e)
            return jsonify({"error": "Failed to delete meal"}), 500

    @api.route("/gym", methods=["GET", "POST"])
    def gym():
        """Gym tracker endpoints."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        gym_service = coordinator.get_service("gym_tracker")
        if not gym_service:
            return jsonify({"error": "Gym service not available"}), 503

        if request.method == "POST":
            data = request.get_json()
            workout_type = data.get("workout_type", "Cardio")
            duration = data.get("duration")

            if not duration:
                return jsonify({"error": "Duration is required"}), 400

            try:
                # Log as cardio workout for simplicity
                entry = gym_service.log_cardio_workout(
                    user_id=user_id,
                    cardio_type=workout_type.lower(),
                    duration_minutes=int(duration),
                    distance_km=0,
                    timestamp=datetime.now(),
                )
                logger.info(
                    "Workout logged: %s - %smin for user %s",
                    workout_type,
                    duration,
                    user_id,
                )

                return (
                    jsonify(
                        {
                            "success": True,
                            "message": "Workout logged successfully",
                            "entry": entry,
                        }
                    ),
                    201,
                )
            except Exception as e:
                logger.error("Failed to log workout: %s", e)
                return jsonify({"error": "Failed to log workout"}), 500

        # GET request
        try:
            workouts = gym_service.get_entries_by_date_range(
                user_id,
                datetime.now().replace(hour=0, minute=0, second=0),
                datetime.now(),
            )
            return jsonify({"workouts": workouts or []}), 200
        except Exception as e:
            logger.error("Failed to fetch workouts: %s", e)
            return jsonify({"workouts": []}), 200

    @api.route("/gym/<int:workout_id>", methods=["DELETE"])
    def delete_workout(workout_id):
        """Delete workout entry."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        gym_service = coordinator.get_service("gym_tracker")
        if not gym_service:
            return jsonify({"error": "Gym service not available"}), 503

        try:
            gym_service.delete_entry(workout_id)
            logger.info("Workout %s deleted for user %s", workout_id, user_id)

            return (
                jsonify({"success": True, "message": "Workout deleted successfully"}),
                200,
            )
        except Exception as e:
            logger.error("Failed to delete workout: %s", e)
            return jsonify({"error": "Failed to delete workout"}), 500

    @api.route("/tamagotchi/health", methods=["GET"])
    def tamagotchi_health():
        """Get Tamagotchi health status."""
        user_id = require_auth()
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        try:
            # Get actual pet health from coordinator
            pet_health = coordinator.get_pet_health(user_id)

            return (
                jsonify(
                    {
                        "health": pet_health.get("overall_health", 50),
                        "status": pet_health.get("status", "okay"),
                        "message": pet_health.get("message", ""),
                        "water_score": pet_health.get("water_score", 0),
                        "food_score": pet_health.get("food_score", 0),
                        "exercise_score": pet_health.get("exercise_score", 0),
                    }
                ),
                200,
            )
        except Exception as e:
            logger.error("Failed to get pet health: %s", e)
            return (
                jsonify(
                    {
                        "health": 50,
                        "status": "okay",
                        "message": "Unable to calculate health",
                    }
                ),
                200,
            )

    logger.info("API Blueprint created successfully")
    return api
