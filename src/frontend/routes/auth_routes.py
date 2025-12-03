"""Authentication routes for login, register, and logout."""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

logger = logging.getLogger(__name__)


def create_auth_routes(coordinator):
    """Create and configure authentication routes."""
    auth = Blueprint("auth", __name__)

    @auth.route("/")
    def index():
        """Redirect to home or login."""
        if "user_id" in session:
            return redirect(url_for("pages.home"))
        return redirect(url_for("auth.login"))

    @auth.route("/login", methods=["GET", "POST"])
    def login():
        """Login page."""
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            try:
                # Use authentication service from coordinator
                result = coordinator.authenticate_user(email, password)
                if result.get("success"):
                    session["user_id"] = result["user_id"]
                    session["email"] = result.get("email", email)
                    flash("Login successful!", "success")
                    return redirect(url_for("pages.home"))
                else:
                    flash("Invalid credentials. Please try again.", "error")
                    return render_template("login.html")
            except Exception as e:
                logger.error("Login failed: %s", e)
                flash("Invalid credentials. Please try again.", "error")
                return render_template("login.html")

        return render_template("login.html")

    @auth.route("/register", methods=["GET", "POST"])
    def register():
        """Registration page."""
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")

            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return render_template("register.html")

            try:
                # Use authentication service from coordinator
                result = coordinator.register_user(
                    email=email,
                    password=password,
                    daily_water_goal=2000,
                    daily_calorie_goal=2000,
                    weekly_exercise_goal=3,
                )
                if result.get("success"):
                    flash("Registration successful! Please log in.", "success")
                    return redirect(url_for("auth.login"))
                else:
                    flash(
                        f"Registration failed: {result.get('error', 'Unknown error')}",
                        "error",
                    )
                    return render_template("register.html")
            except Exception as e:
                logger.error("Registration failed: %s", e)
                flash("Registration failed. Email may already be in use.", "error")
                return render_template("register.html")

        return render_template("register.html")

    @auth.route("/logout")
    def logout():
        """Logout user."""
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("auth.login"))

    return auth
