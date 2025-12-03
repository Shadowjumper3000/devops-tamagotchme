"""Frontend utility functions and decorators."""

import logging
from functools import wraps
from flask import session, flash, redirect, url_for

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require login for routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


def require_auth():
    """Check if user is authenticated for API routes."""
    if "user_id" not in session:
        return None
    return session["user_id"]


def get_user_from_session():
    """Get current user info from session."""
    return {"user_id": session.get("user_id"), "email": session.get("email")}
