"""Web application with REST API for the Life Planner (placeholder)."""

import logging
from flask import Flask, jsonify

logger = logging.getLogger(__name__)


class WebApp:
    """Flask web application for Life Planner (placeholder)."""

    def __init__(self, config, coordinator):
        """Initialize the web application."""
        self.config = config
        self.coordinator = coordinator
        self.app = Flask(__name__)
        self._setup_routes()
        logger.info("Web application initialized")

    def _setup_routes(self):
        """Setup basic routes including health check."""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint for monitoring."""
            return jsonify({
                'status': 'healthy',
                'app_name': self.config.app_name,
                'version': self.config.version
            }), 200
        
        @self.app.route('/', methods=['GET'])
        def index():
            """Index endpoint."""
            return jsonify({
                'message': 'Life Planner API',
                'version': self.config.version,
                'endpoints': {
                    'health': '/health'
                }
            }), 200

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """Run the web application."""
        logger.info("Starting Flask application on %s:%s", host, port)
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """Get the Flask application instance."""
        return self.app
