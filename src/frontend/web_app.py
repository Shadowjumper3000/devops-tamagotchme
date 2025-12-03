"""Web application with REST API for the Life Planner."""

import logging
import os
from flask import Flask, jsonify
from .routes import create_auth_routes, create_page_routes
from .api import create_api_blueprint

logger = logging.getLogger(__name__)


class WebApp:
    """Flask web application for Tamagotchi Tracker."""

    def __init__(self, config, coordinator):
        """Initialize the web application."""
        self.config = config
        self.coordinator = coordinator

        # Get the directory of this file to properly locate templates and static
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(current_dir, "templates")
        static_dir = os.path.join(current_dir, "static")

        self.app = Flask(
            __name__, template_folder=template_dir, static_folder=static_dir
        )
        self.app.secret_key = getattr(
            config, "secret_key", "dev-secret-key-change-in-production"
        )

        self._register_blueprints()
        self._register_health_endpoint()
        logger.info("Web application initialized")

    def _register_health_endpoint(self):
        """Register health check endpoint."""

        @self.app.route("/health")
        def health():
            """Health check endpoint for Docker and monitoring."""
            try:
                # Basic health check - just verify app is running
                return (
                    jsonify(
                        {
                            "status": "healthy",
                            "app": self.config.app_name,
                            "version": self.config.version,
                        }
                    ),
                    200,
                )
            except Exception as e:
                logger.error("Health check failed: %s", e)
                return jsonify({"status": "unhealthy", "error": str(e)}), 503

    def _register_blueprints(self):
        """Register all blueprints."""
        # Register authentication routes
        auth_bp = create_auth_routes(self.coordinator)
        self.app.register_blueprint(auth_bp)
        logger.info("Auth routes registered")

        # Register page routes
        pages_bp = create_page_routes(self.coordinator)
        self.app.register_blueprint(pages_bp)
        logger.info("Page routes registered")

        # Register API blueprint
        api_bp = create_api_blueprint(self.coordinator)
        self.app.register_blueprint(api_bp, url_prefix="/api")
        logger.info("API blueprint registered at /api")

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """Run the web application."""
        logger.info("Starting web application on %s:%s", host, port)
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """Get the Flask application instance."""
        return self.app
