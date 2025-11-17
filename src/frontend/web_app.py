"""Web application with REST API for the Life Planner (placeholder)."""

import logging

logger = logging.getLogger(__name__)


class WebApp:
    """Flask web application for Life Planner (placeholder)."""

    def __init__(self, config, coordinator):
        """Initialize the web application."""
        self.config = config
        self.coordinator = coordinator
        logger.info("Web application placeholder initialized")

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """Run the web application (placeholder)."""
        logger.info("WebApp.run() called - placeholder implementation")
        print(f"WebApp placeholder: would start on {host}:{port} (debug={debug})")

    def get_app(self):
        """Get the Flask application instance (placeholder)."""
        logger.info("WebApp.get_app() called - placeholder implementation")
        return None
