"""User authentication models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship

from ...core.database import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # User profile
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Pet health settings (user preferences)
    daily_water_goal = Column(Integer, default=2000, nullable=False)  # ml
    daily_calorie_goal = Column(Integer, default=2000, nullable=False)
    weekly_exercise_goal = Column(Integer, default=3, nullable=False)  # times per week

    # Relationships
    water_entries = relationship("WaterEntry", back_populates="user", cascade="all, delete-orphan")
    food_entries = relationship("FoodEntry", back_populates="user", cascade="all, delete-orphan")
    workout_entries = relationship("WorkoutEntry", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

    def to_dict(self):
        """Convert user to dictionary (excluding password)."""
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "goals": {
                "daily_water_ml": self.daily_water_goal,
                "daily_calories": self.daily_calorie_goal,
                "weekly_exercise": self.weekly_exercise_goal,
            }
        }