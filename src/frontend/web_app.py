"""Web application with REST API for the Life Planner."""

import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)
from datetime import datetime
from functools import wraps
from .api import create_api_blueprint

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


class WebApp:
    """Flask web application for Tamagotchi Tracker."""

    def __init__(self, config, coordinator):
        """Initialize the web application."""
        self.config = config
        self.coordinator = coordinator
        self.app = Flask(__name__, template_folder="templates", static_folder="static")
        self.app.secret_key = config.get(
            "secret_key", "dev-secret-key-change-in-production"
        )

        self._register_routes()
        self._register_blueprints()
        logger.info("Web application initialized")

    def _register_routes(self):
        """Register all routes."""

        @self.app.route("/")
        def index():
            """Redirect to home or login."""
            if "user_id" in session:
                return redirect(url_for("home"))
            return redirect(url_for("login"))

        @self.app.route("/login", methods=["GET", "POST"])
        def login():
            """Login page."""
            if request.method == "POST":
                username = request.form.get("username")
                password = request.form.get("password")

                # TODO: Implement actual authentication
                # For now, just set session
                session["user_id"] = 1
                session["username"] = username
                flash("Login successful!", "success")
                return redirect(url_for("home"))

            return render_template("login.html")

        @self.app.route("/register", methods=["GET", "POST"])
        def register():
            """Registration page."""
            if request.method == "POST":
                username = request.form.get("username")
                email = request.form.get("email")
                password = request.form.get("password")
                confirm_password = request.form.get("confirm_password")

                if password != confirm_password:
                    flash("Passwords do not match!", "error")
                    return render_template("register.html")

                # TODO: Implement actual registration
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("login"))

            return render_template("register.html")

        @self.app.route("/logout")
        def logout():
            """Logout user."""
            session.clear()
            flash("You have been logged out.", "info")
            return redirect(url_for("login"))

        @self.app.route("/home")
        @login_required
        def home():
            """Home page with Tamagotchi."""
            # TODO: Get actual data from services
            tamagotchi = {"name": "TamagotchMe", "health": 85}
            stats = {"water_today": 1500, "calories_today": 1800, "workout_minutes": 45}
            return render_template(
                "home.html",
                username=session.get("username"),
                tamagotchi=tamagotchi,
                stats=stats,
            )

        @self.app.route("/water")
        @login_required
        def water_page():
            """Water tracker page."""
            # TODO: Get actual analytics from water service
            analytics = {
                "today_total": 1500,
                "today_percentage": 75,
                "daily_goal": 2000,
                "weekly_avg": 1650,
                "weekly_total": 11550,
                "streak": 5,
            }
            history = []
            return render_template("water.html", analytics=analytics, history=history)

        @self.app.route("/food")
        @login_required
        def food_page():
            """Food tracker page."""
            # TODO: Get actual analytics from food service
            analytics = {
                "today_calories": 1800,
                "calorie_percentage": 90,
                "calorie_goal": 2000,
                "today_protein": 120,
                "protein_percentage": 80,
                "today_carbs": 200,
                "carbs_percentage": 75,
                "today_fats": 60,
                "fats_percentage": 70,
            }
            meals = []
            return render_template("food.html", analytics=analytics, meals=meals)

        @self.app.route("/gym")
        @login_required
        def gym_page():
            """Gym tracker page."""
            # TODO: Get actual analytics from gym service
            analytics = {
                "today_minutes": 45,
                "goal_percentage": 75,
                "daily_goal": 60,
                "weekly_minutes": 240,
                "weekly_workouts": 5,
                "calories_burned": 350,
                "streak": 3,
            }
            workouts = []
            return render_template("gym.html", analytics=analytics, workouts=workouts)

    def _register_blueprints(self):
        """Register API blueprint."""
        api_bp = create_api_blueprint(self.coordinator)
        if api_bp:
            self.app.register_blueprint(api_bp, url_prefix="/api")
            logger.info("API blueprint registered at /api")

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        """Run the web application."""
        logger.info(f"Starting web application on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        """Get the Flask application instance."""
        return self.app
