"""Authentication repository for user database operations."""

import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .models import User
from ...shared.database_interface import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for user database operations."""

    def __init__(self, db_session: Session):
        """Initialize repository with User model."""
        super().__init__(db_session, User)

    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        try:
            return (
                self.db_session.query(User)
                .filter(User.email == email.lower())
                .first()
            )
        except Exception as e:
            logger.error(f"Error finding user by email: {e}")
            return None

    def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email exists, False otherwise
        """
        return self.find_by_email(email) is not None

    def create_user(self, email: str, password_hash: str, **kwargs) -> Optional[User]:
        """
        Create a new user.
        
        Args:
            email: User's email address
            password_hash: Hashed password
            **kwargs: Additional user fields
            
        Returns:
            Created User object or None if failed
        """
        try:
            user = User(
                email=email.lower(),
                password_hash=password_hash,
                **kwargs
            )
            
            self.db_session.add(user)
            self.db_session.commit()
            self.db_session.refresh(user)
            
            logger.info(f"User created: {email}")
            return user
            
        except IntegrityError as e:
            self.db_session.rollback()
            logger.error(f"User creation failed - email already exists: {email}")
            return None
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"User creation failed: {e}")
            return None

    def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User's ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.get_by_id(user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update last login: {e}")
            return False

    def update_user_goals(
        self,
        user_id: int,
        daily_water_goal: Optional[int] = None,
        daily_calorie_goal: Optional[int] = None,
        weekly_exercise_goal: Optional[int] = None
    ) -> Optional[User]:
        """
        Update user's health goals.
        
        Args:
            user_id: User's ID
            daily_water_goal: Daily water intake goal in ml
            daily_calorie_goal: Daily calorie goal
            weekly_exercise_goal: Weekly exercise frequency goal
            
        Returns:
            Updated User object or None if failed
        """
        try:
            user = self.get_by_id(user_id)
            if not user:
                return None
            
            if daily_water_goal is not None:
                user.daily_water_goal = daily_water_goal
            if daily_calorie_goal is not None:
                user.daily_calorie_goal = daily_calorie_goal
            if weekly_exercise_goal is not None:
                user.weekly_exercise_goal = weekly_exercise_goal
            
            user.updated_at = datetime.utcnow()
            self.db_session.commit()
            self.db_session.refresh(user)
            
            logger.info(f"Updated goals for user {user_id}")
            return user
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update user goals: {e}")
            return None

    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User's ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            user = self.get_by_id(user_id)
            if user:
                user.is_active = False
                user.updated_at = datetime.utcnow()
                self.db_session.commit()
                logger.info(f"User {user_id} deactivated")
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to deactivate user: {e}")
            return False

    def get_active_users_count(self) -> int:
        """
        Get count of active users.
        
        Returns:
            Number of active users
        """
        try:
            return (
                self.db_session.query(User)
                .filter(User.is_active == True)
                .count()
            )
        except Exception as e:
            logger.error(f"Failed to count active users: {e}")
            return 0
