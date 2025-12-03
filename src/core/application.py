"""Main application class that coordinates all modules."""

import logging
from typing import Dict, Any

from .config import Config
from .coordinator import ModuleCoordinator
from .database import DatabaseManager
from src.frontend.web_app import WebApp


logger = logging.getLogger(__name__)


class LifePlannerApp:
    """Main application class for the Life Planner."""

    def __init__(self, config: Config):
        """Initialize the application with configuration."""
        self.config = config
        self.database_manager = DatabaseManager(config)
        self.coordinator = ModuleCoordinator(config, self.database_manager)
        self.web_app = WebApp(config, self.coordinator)

        logger.info("Life Planner Application initialized")

    def run(self):
        """Run the application."""
        try:
            # Initialize database
            self.database_manager.initialize()

            # Initialize modules through coordinator
            self.coordinator.initialize_modules()

            # Start the web application
            logger.info(
                "Starting web application on %s:%s", self.config.host, self.config.port
            )
            self.web_app.run(
                host=self.config.host, port=self.config.port, debug=self.config.debug
            )

        except Exception as e:
            logger.error("Failed to run application: %s", e)
            raise

    def shutdown(self):
        """Gracefully shutdown the application."""
        logger.info("Shutting down Life Planner Application")

        # Shutdown modules
        self.coordinator.shutdown_modules()

        # Close database connections
        self.database_manager.close()

        logger.info("Application shutdown complete")

    def get_status(self) -> Dict[str, Any]:
        """Get application status."""
        return {
            "app_name": self.config.app_name,
            "version": self.config.version,
            "modules": self.coordinator.get_module_status(),
            "database": self.database_manager.get_status(),
        }

    def health_check(self) -> bool:
        """Perform a health check of the application."""
        try:
            db_session = self.database_manager.get_session()
            db_session.execute("SELECT 1")
            db_session.close()
            return True
        except Exception as e:
            logger.error("Health check failed: %s", e)
            return False
