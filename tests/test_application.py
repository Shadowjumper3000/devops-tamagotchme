"""Unit tests for Core Application."""

import pytest
from unittest.mock import Mock, patch
from src.core.application import LifePlannerApp
from src.core.config import Config


class TestLifePlannerApp:
    """Test suite for LifePlannerApp."""

    @pytest.fixture
    def test_config(self):
        """Create a test configuration."""
        return Config(
            database_url="sqlite:///:memory:",
            database_path=":memory:",
            host="127.0.0.1",
            port=8080,
            debug=False,
            app_name="Test Life Planner",
            version="1.0.0",
            log_level="INFO",
            food_tracker_enabled=True,
            water_tracker_enabled=True,
            gym_tracker_enabled=True
        )

    def test_app_initialization(self, test_config):
        """Test that application initializes correctly."""
        app = LifePlannerApp(test_config)
        
        assert app.config == test_config
        assert app.database_manager is not None
        assert app.coordinator is not None
        assert app.web_app is not None

    def test_app_initialization_creates_components(self, test_config):
        """Test that all components are created during initialization."""
        app = LifePlannerApp(test_config)
        
        # Verify database manager
        assert app.database_manager.config == test_config
        
        # Verify coordinator
        assert app.coordinator.config == test_config
        assert app.coordinator.database_manager == app.database_manager
        
        # Verify web app
        assert app.web_app.config == test_config

    @patch('src.core.application.WebApp')
    def test_run_initializes_database_first(self, mock_webapp, test_config, db_session):
        """Test that database is initialized before modules."""
        app = LifePlannerApp(test_config)
        app.database_manager.SessionLocal = Mock(return_value=db_session)
        
        # Mock the web app run to prevent actual Flask startup
        app.web_app.run = Mock()
        
        # Run the application
        app.run()
        
        # Verify database was initialized
        assert app.database_manager.engine is not None
        
        # Verify web app was started
        app.web_app.run.assert_called_once()

    def test_get_status(self, test_config):
        """Test getting application status."""
        app = LifePlannerApp(test_config)
        
        status = app.get_status()
        
        assert "app_name" in status
        assert "version" in status
        assert "modules" in status
        assert "database" in status
        assert status["app_name"] == test_config.app_name
        assert status["version"] == test_config.version

    def test_health_check_before_init(self, test_config):
        """Test health check before database initialization."""
        app = LifePlannerApp(test_config)
        
        # Health check should fail before initialization
        result = app.health_check()
        
        assert result is False

    def test_shutdown(self, test_config):
        """Test application shutdown."""
        app = LifePlannerApp(test_config)
        
        # Should not raise any exceptions
        app.shutdown()
