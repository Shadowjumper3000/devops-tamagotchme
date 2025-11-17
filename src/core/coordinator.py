"""Module coordinator for managing all tracker modules."""

import logging
from typing import Dict, Any

from .config import Config
from .database import DatabaseManager
from ..modules.food_tracker.service import FoodTrackerService
from ..modules.water_tracker.service import WaterTrackerService
from ..modules.gym_tracker.service import GymTrackerService


logger = logging.getLogger(__name__)


class ModuleCoordinator:
    """Coordinates all tracker modules and their interactions."""

    def __init__(self, config: Config, database_manager: DatabaseManager):
        """Initialize the coordinator with configuration and database manager."""
        self.config = config
        self.database_manager = database_manager

        # Initialize services
        self.services = {}
        self._initialize_services()

        logger.info("Module Coordinator initialized")

    def _initialize_services(self):
        """Initialize all enabled services."""
        if self.config.food_tracker_enabled:
            self.services["food_tracker"] = FoodTrackerService(
                self.database_manager.get_session()
            )

        if self.config.water_tracker_enabled:
            self.services["water_tracker"] = WaterTrackerService(
                self.database_manager.get_session()
            )

        if self.config.gym_tracker_enabled:
            self.services["gym_tracker"] = GymTrackerService(
                self.database_manager.get_session()
            )

    def initialize_modules(self):
        """Initialize all modules."""
        for name, service in self.services.items():
            try:
                service.initialize()
                logger.info("Initialized %s module", name)
            except Exception as e:
                logger.error("Failed to initialize %s module: %s", name, e)
                raise

    def shutdown_modules(self):
        """Shutdown all modules."""
        for name, service in self.services.items():
            try:
                service.shutdown()
                logger.info("Shutdown %s module", name)
            except Exception as e:
                logger.error("Error shutting down %s module: %s", name, e)

    def get_service(self, service_name: str):
        """Get a service by name."""
        return self.services.get(service_name)

    def get_module_status(self) -> Dict[str, Any]:
        """Get status of all modules."""
        status = {}
        for name, service in self.services.items():
            try:
                status[name] = service.get_status()
            except Exception as e:
                status[name] = {"error": str(e)}
        return status

    def get_daily_summary(self) -> Dict[str, Any]:
        """Get daily summary from all modules."""
        summary = {}

        if "food_tracker" in self.services:
            summary["food"] = self.services["food_tracker"].get_daily_summary()

        if "water_tracker" in self.services:
            summary["water"] = self.services["water_tracker"].get_daily_summary()

        if "gym_tracker" in self.services:
            summary["gym"] = self.services["gym_tracker"].get_daily_summary()

        return summary

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Get weekly summary from all modules."""
        summary = {}

        if "food_tracker" in self.services:
            summary["food"] = self.services["food_tracker"].get_weekly_summary()

        if "water_tracker" in self.services:
            summary["water"] = self.services["water_tracker"].get_weekly_summary()

        if "gym_tracker" in self.services:
            summary["gym"] = self.services["gym_tracker"].get_weekly_summary()

        return summary
