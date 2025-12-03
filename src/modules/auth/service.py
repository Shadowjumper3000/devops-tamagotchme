"""Authentication service."""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import User
from .repository import UserRepository
from .utils import PasswordHasher

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass


class AuthService:
    """Ultra-simple authentication service."""

    def __init__(self, db_session: Session):
        """Initialize authentication service."""
        self.db_session = db_session
        self.user_repository = UserRepository(db_session)
        self.password_hasher = PasswordHasher()

    def register(
        self,
        email: str,
        password: str,
        daily_water_goal: int = 2000,
        daily_calorie_goal: int = 2000,
        weekly_exercise_goal: int = 3
    ) -> Dict[str, Any]:
        """Register a new user - no validation."""
        try:
            # Only check if email already exists
            if self.user_repository.email_exists(email):
                raise AuthenticationError("Email already registered")

            # Hash password (keep for basic security)
            password_hash = self.password_hasher.hash_password(password)

            # Create user
            user = self.user_repository.create_user(
                email=email,
                password_hash=password_hash,
                daily_water_goal=daily_water_goal,
                daily_calorie_goal=daily_calorie_goal,
                weekly_exercise_goal=weekly_exercise_goal
            )

            if not user:
                raise AuthenticationError("Failed to create user")

            logger.info(f"User registered: {email}")

            return {
                "success": True,
                "message": "Registration successful",
                "user_id": user.id,
                "user": user.to_dict()
            }

        except AuthenticationError as e:
            logger.warning(f"Registration failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during registration: {e}")
            raise AuthenticationError("Registration failed due to server error")

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login a user - simple check."""
        try:
            # Find user
            user = self.user_repository.find_by_email(email)

            if not user:
                raise AuthenticationError("Invalid email or password")

            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("Account is deactivated")

            # Check password
            if not self.password_hasher.verify_password(password, user.password_hash):
                raise AuthenticationError("Invalid email or password")

            # Update last login
            self.user_repository.update_last_login(user.id)

            logger.info(f"User logged in: {email}")

            return {
                "success": True,
                "message": "Login successful",
                "user_id": user.id,
                "user": user.to_dict()
            }

        except AuthenticationError as e:
            logger.warning(f"Login failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError("Login failed due to server error")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        user = self.user_repository.get_by_id(user_id)
        return user.to_dict() if user else None

    def update_user_goals(
        self,
        user_id: int,
        daily_water_goal: Optional[int] = None,
        daily_calorie_goal: Optional[int] = None,
        weekly_exercise_goal: Optional[int] = None
    ) -> Dict[str, Any]:
        """Update user's health goals."""
        try:
            user = self.user_repository.update_user_goals(
                user_id,
                daily_water_goal=daily_water_goal,
                daily_calorie_goal=daily_calorie_goal,
                weekly_exercise_goal=weekly_exercise_goal
            )

            if not user:
                raise AuthenticationError("Failed to update goals")

            return {
                "success": True,
                "message": "Goals updated successfully",
                "user": user.to_dict()
            }

        except AuthenticationError as e:
            logger.warning(f"Goal update failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error updating goals: {e}")
            raise AuthenticationError("Goal update failed due to server error")

    def get_status(self) -> Dict[str, Any]:
        """Get authentication service status."""
        return {
            "service": "AuthService",
            "status": "operational",
            "active_users": self.user_repository.get_active_users_count()
        }