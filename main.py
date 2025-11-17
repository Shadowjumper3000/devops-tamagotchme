#!/usr/bin/env python3
"""
Life Planner Application - Main Entry Point

A modular monolith application for tracking food, water intake, and gym activities.
"""

import sys
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import after path modification
from src.core.application import LifePlannerApp  # noqa: E402
from src.core.config import get_config  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    try:
        logger.info("Starting Life Planner Application...")

        # Load configuration
        config = get_config()

        # Initialize and run the application
        app = LifePlannerApp(config)
        app.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
