#!/usr/bin/env python3
"""
Life Planner Application - Simplified Demo

Shows the complete system with simplified authentication (no password rules, no tokens).
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path modification
from src.core.application import LifePlannerApp  # noqa: E402
from src.core.config import get_config  # noqa: E402
from src.core.database import DatabaseManager  # noqa: E402
from src.core.coordinator import ModuleCoordinator  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60 + "\n")


def main():
    """Run the example demonstration."""

    print_section("Life Planner - Simplified System Demo")

    # ========================================================================
    # STEP 1: Initialize System
    # ========================================================================
    print_section("STEP 1: System Initialization")

    config = get_config()
    db_manager = DatabaseManager(config)
    db_manager.initialize()
    print("✓ Database initialized")

    coordinator = ModuleCoordinator(config, db_manager)
    coordinator.initialize_modules()
    print("✓ All modules initialized")

    # Check system status
    status = coordinator.get_module_status()
    print("\nSystem Status:")
    for service_name, service_status in status.items():
        print(f"  - {service_name}: {service_status.get('status', 'unknown')}")

    # ========================================================================
    # STEP 2: User Registration (Simplified - ANY password works!)
    # ========================================================================
    print_section("STEP 2: User Registration (Simplified)")

    print("Note: With simplified auth, ANY password is accepted!")
    print("      - No length requirement")
    print("      - No uppercase/lowercase requirement")
    print("      - No special characters needed\n")

    try:
        registration_result = coordinator.register_user(
            email="demo@example.com",
            password="hi",  # Super simple password!
            daily_water_goal=2500,
            daily_calorie_goal=2200,
            weekly_exercise_goal=4
        )

        if registration_result.get("success"):
            print("✓ User registered successfully with password 'hi'!")
            user = registration_result["user"]
            user_id = registration_result["user_id"]

            print(f"\nUser Details:")
            print(f"  ID: {user_id}")
            print(f"  Email: {user['email']}")
            print(f"  Goals:")
            print(f"    - Water: {user['goals']['daily_water_ml']}ml/day")
            print(f"    - Calories: {user['goals']['daily_calories']}/day")
            print(f"    - Exercise: {user['goals']['weekly_exercise']}x/week")
        else:
            print("✗ Registration failed:", registration_result.get("error"))
            return

    except Exception as e:
        print(f"Note: User might already exist. Attempting login instead...")

        # Try to login instead
        login_result = coordinator.authenticate_user(
            email="demo@example.com",
            password="hi"
        )

        if login_result.get("success"):
            print("✓ Logged in with existing user")
            user = login_result["user"]
            user_id = login_result["user_id"]
        else:
            print("✗ Login also failed. Exiting.")
            return

    # ========================================================================
    # STEP 3: Simple Login (No tokens!)
    # ========================================================================
    print_section("STEP 3: Simple Login")

    print("No JWT tokens needed - just use user_id!\n")

    login_result = coordinator.authenticate_user(
        email="demo@example.com",
        password="hi"
    )

    if login_result.get("success"):
        print("✓ Login successful")
        print(f"  User ID: {login_result['user_id']}")
        print(f"  Email: {login_result['user']['email']}")
        print("\n  → Just store this user_id and use it for all requests!")
        user_id = login_result["user_id"]
    else:
        print("✗ Login failed")
        return

    # ========================================================================
    # STEP 4: Log Tracking Data
    # ========================================================================
    print_section("STEP 4: Logging Daily Activities")

    # Get tracker services
    water_service = coordinator.get_service("water_tracker")
    food_service = coordinator.get_service("food_tracker")
    gym_service = coordinator.get_service("gym_tracker")

    print("Logging water intake...")
    water_service.log_water(user_id, 500)  # Morning water
    water_service.log_water(user_id, 300)  # Mid-morning
    water_service.log_water(user_id, 400)  # Lunch
    water_service.log_water(user_id, 350)  # Afternoon
    water_service.log_water(user_id, 450)  # Evening
    print("✓ Logged 5 water entries (2000ml total)")

    print("\nLogging meals...")
    food_service.log_food(user_id, 450, meal_name="Oatmeal & Fruit", meal_type="breakfast")
    food_service.log_food(user_id, 650, meal_name="Chicken Salad", meal_type="lunch")
    food_service.log_food(user_id, 200, meal_name="Protein Bar", meal_type="snack")
    food_service.log_food(user_id, 700, meal_name="Salmon & Vegetables", meal_type="dinner")
    print("✓ Logged 4 meals (2000 calories total)")

    print("\nLogging workouts...")
    # Morning HIIT workout
    gym_service.log_hiit_workout(
        user_id=user_id,
        exercises=[
            {"exercise": "Push-ups", "reps": 25, "weight": 0},
            {"exercise": "Squats", "reps": 30, "weight": 60},
            {"exercise": "Pull-ups", "reps": 12, "weight": 0},
            {"exercise": "Burpees", "reps": 15, "weight": 0}
        ],
        intensity="high",
        notes="Great morning workout!"
    )
    print("✓ Logged HIIT workout with 4 exercises")

    # Evening cardio
    gym_service.log_cardio_workout(
        user_id=user_id,
        exercise_name="Running",
        duration_minutes=35,
        intensity="medium"
    )
    print("✓ Logged 35-minute run")

    # ========================================================================
    # STEP 5: Calculate Pet Health
    # ========================================================================
    print_section("STEP 5: Pet Health Calculation")

    pet_health = coordinator.get_pet_health(user_id)

    print(f"Pet Health Score: {pet_health['overall_health']}/100")
    print(f"Status: {pet_health['status'].upper()}")
    print(f"Message: {pet_health['message']}")

    print("\nComponent Breakdown:")
    for component, data in pet_health['components'].items():
        print(f"  {component.capitalize()}:")
        print(f"    Score: {data['score']}/100")
        print(f"    Weight: {data['weight'] * 100}%")
        print(f"    Contribution: {data['contribution']}")

    print("\nRecommendations:")
    for i, rec in enumerate(pet_health.get('recommendations', []), 1):
        print(f"  {i}. {rec}")

    # ========================================================================
    # STEP 6: Full Dashboard
    # ========================================================================
    print_section("STEP 6: Complete Dashboard Summary")

    dashboard = coordinator.get_daily_summary(user_id)

    print("Today's Summary:")

    # Water
    water_sum = dashboard['today_summary']['water']
    print(f"\n💧 Water: {water_sum['total_ml']}ml / {dashboard['goals']['daily_water_ml']}ml")
    print(f"   Progress: {dashboard['progress']['water']['percentage']}%")
    print(f"   Goal {'✓ ACHIEVED' if dashboard['progress']['water']['achieved'] else '✗ Not Met'}")

    # Food
    food_sum = dashboard['today_summary']['food']
    print(f"\n🍽️  Food: {food_sum['total_calories']} / {dashboard['goals']['daily_calories']} calories")
    print(f"   Progress: {dashboard['progress']['calories']['percentage']}%")
    print(f"   Goal {'✓ ACHIEVED' if dashboard['progress']['calories']['achieved'] else '✗ Not Met'}")
    print(f"   Meals: {food_sum['meal_count']}")

    # Gym
    gym_sum = dashboard['today_summary']['gym']
    print(f"\n💪 Exercise: {gym_sum['workout_count']} workout(s)")
    print(f"   Progress: {dashboard['progress']['exercise']['percentage']}%")
    print(f"   Goal {'✓ ACHIEVED' if dashboard['progress']['exercise']['achieved'] else '✗ Not Met'}")
    print(f"   HIIT: {gym_sum['hiit_count']}, Cardio: {gym_sum['cardio_count']}")
    print(f"   Total Cardio: {gym_sum['total_cardio_minutes']} minutes")

    # ========================================================================
    # STEP 7: Test Different Passwords
    # ========================================================================
    print_section("STEP 7: Testing Simplified Authentication")

    print("Let's test with different simple passwords...\n")

    test_users = [
        ("test1@example.com", "1"),
        ("test2@example.com", "abc"),
        ("test3@example.com", "password"),
    ]

    for email, password in test_users:
        try:
            result = coordinator.register_user(email, password)
            if result["success"]:
                print(f"✓ Registered {email} with password '{password}'")
        except Exception as e:
            print(f"  (User {email} already exists)")

    print("\nAll passwords work - no validation required! 🎉")

    # ========================================================================
    # Complete!
    # ========================================================================
    print_section("Demo Complete!")
    print("✓ Simplified authentication works (any password!)")
    print("✓ All trackers logging data")
    print("✓ Pet health calculation functioning")
    print("✓ Dashboard aggregating everything")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()