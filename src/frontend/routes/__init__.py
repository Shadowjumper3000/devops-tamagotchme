"""Frontend routes package."""

from .auth_routes import create_auth_routes
from .page_routes import create_page_routes

__all__ = ["create_auth_routes", "create_page_routes"]
