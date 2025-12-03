"""Module coordinator for managing all services including auth and business logic."""

import logging
from typing import Dict, Any, Optional

from .config import Config
from .database import DatabaseManager
from .dashboard_service import DashboardService
from ..modules.auth.service import AuthService
from ..modules.food_tracker.service import FoodTrackerService
from ..modules.water_tracker.service import WaterTrackerService
from ..modules.gym_tracker.service import GymTrackerService


logger = logging.getLogger(__name__)


class ModuleCoordinator:
    """
    Enhanced coordinator that manages all services and business logic.
    
    This coordinator includes:
    - Authentication service (simplified)
    - All tracker services (water, food, gym)
    - Dashboard service (business logic layer)
    """

    def __init__(self, config: Config, database_manager: DatabaseManager):
        """Initialize the coordinator with configuration and database manager."""
        self.config = config
        self.database_manager = database_manager

        # Initialize services
        self.services = {}
        self.auth_service = None
        self.dashboard_service = None

        self._initialize_services()

        logger.info("Enhanced Module Coordinator initialized")

    def _initialize_services(self):
        """Initialize all enabled services."""
        # Get a shared database session for all services
        db_session = self.database_manager.get_session()

        # Initialize authentication service (always enabled)
        self.auth_service = AuthService(db_session)
        logger.info("Authentication service initialized")

        # Initialize tracker services based on configuration
        if self.config.food_tracker_enabled:
            self.services["food_tracker"] = FoodTrackerService(db_session)
            logger.info("Food tracker service initialized")

        if self.config.water_tracker_enabled:
            self.services["water_tracker"] = WaterTrackerService(db_session)
            logger.info("Water tracker service initialized")

        if self.config.gym_tracker_enabled:
            self.services["gym_tracker"] = GymTrackerService(db_session)
            logger.info("Gym tracker service initialized")

        # Initialize dashboard service (business logic layer)
        self.dashboard_service = DashboardService(db_session)
        logger.info("Dashboard service initialized")

    def initialize_modules(self):
        """Initialize all modules."""
        # Initialize tracker services
        for name, service in self.services.items():
            try:
                service.initialize()
                logger.info("Initialized %s module", name)
            except Exception as e:
                logger.error("Failed to initialize %s module: %s", name, e)
                raise

        logger.info("All modules initialized successfully")

    def shutdown_modules(self):
        """Shutdown all modules."""
        for name, service in self.services.items():
            try:
                service.shutdown()
                logger.info("Shutdown %s module", name)
            except Exception as e:
                logger.error("Error shutting down %s module: %s", name, e)

    def get_service(self, service_name: str):
        """
        Get a service by name.

        Args:
            service_name: Name of the service to retrieve

        Returns:
            Service instance or None if not found
        """
        return self.services.get(service_name)

    def get_auth_service(self) -> AuthService:
        """
        Get the authentication service.

        Returns:
            AuthService instance
        """
        return self.auth_service

    def get_dashboard_service(self) -> DashboardService:
        """
        Get the dashboard service.

        Returns:
            DashboardService instance
        """
        return self.dashboard_service

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules."""
        status = {}

        # Auth service status
        if self.auth_service:
            try:
                status["auth"] = self.auth_service.get_status()
            except Exception as e:
                status["auth"] = {"error": str(e)}

        # Tracker services status
        for name, service in self.services.items():
            try:
                status[name] = service.get_status()
            except Exception as e:
                status[name] = {"error": str(e)}

        # Dashboard service status
        if self.dashboard_service:
            try:
                status["dashboard"] = self.dashboard_service.get_status()
            except Exception as e:
                status["dashboard"] = {"error": str(e)}

        return status

    def get_daily_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get daily summary from all modules for a specific user.

        Args:
            user_id: User's ID

        Returns:
            Complete daily summary including pet health
        """
        try:
            return self.dashboard_service.get_dashboard_data(user_id)
        except Exception as e:
            logger.error(f"Error getting daily summary for user {user_id}: {e}")
            return {"error": str(e)}

    def get_weekly_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get weekly summary from all modules for a specific user.

        Args:
            user_id: User's ID

        Returns:
            Complete weekly summary with trends
        """
        try:
            return self.dashboard_service.get_weekly_dashboard(user_id)
        except Exception as e:
            logger.error(f"Error getting weekly summary for user {user_id}: {e}")
            return {"error": str(e)}

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user (login) - simplified version.

        Args:
            email: User's email (any format accepted)
            password: User's password (any format accepted)

        Returns:
            Authentication result with user_id
        """
        try:
            return self.auth_service.login(email, password)
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {"success": False, "error": str(e)}

    def register_user(
        self,
        email: str,
        password: str,
        daily_water_goal: int = 2000,
        daily_calorie_goal: int = 2000,
        weekly_exercise_goal: int = 3
    ) -> Dict[str, Any]:
        """
        Register a new user - simplified version.

        Args:
            email: User's email (any format accepted)
            password: User's password (any format accepted)
            daily_water_goal: Daily water goal in ml (default: 2000)
            daily_calorie_goal: Daily calorie goal (default: 2000)
            weekly_exercise_goal: Weekly exercise frequency (default: 3)

        Returns:
            Registration result with user_id
        """
        try:
            return self.auth_service.register(
                email=email,
                password=password,
                daily_water_goal=daily_water_goal,
                daily_calorie_goal=daily_calorie_goal,
                weekly_exercise_goal=weekly_exercise_goal
            )
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return {"success": False, "error": str(e)}

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user data by ID.

        Args:
            user_id: User's ID

        Returns:
            User data if found, None otherwise
        """
        try:
            return self.auth_service.get_user_by_id(user_id)
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            return None

    def update_user_goals(
        self,
        user_id: int,
        daily_water_goal: Optional[int] = None,
        daily_calorie_goal: Optional[int] = None,
        weekly_exercise_goal: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update user's health goals.

        Args:
            user_id: User's ID
            daily_water_goal: New daily water goal in ml
            daily_calorie_goal: New daily calorie goal
            weekly_exercise_goal: New weekly exercise frequency

        Returns:
            Update result
        """
        try:
            return self.auth_service.update_user_goals(
                user_id=user_id,
                daily_water_goal=daily_water_goal,
                daily_calorie_goal=daily_calorie_goal,
                weekly_exercise_goal=weekly_exercise_goal
            )
        except Exception as e:
            logger.error(f"Failed to update goals for user {user_id}: {e}")
            return {"success": False, "error": str(e)}

    def get_pet_health(self, user_id: int) -> Dict[str, Any]:
        """
        Get current pet health for a user.

        This is a convenience method that extracts just the pet health
        from the full dashboard data.

        Args:
            user_id: User's ID

        Returns:
            Pet health data
        """
        try:
            dashboard = self.dashboard_service.get_dashboard_data(user_id)
            return dashboard.get("pet_health", {})
        except Exception as e:
            logger.error(f"Error getting pet health for user {user_id}: {e}")
            return {"error": str(e)}