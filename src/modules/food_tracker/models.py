"""Food tracker data models."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ...core.database import Base


class FoodEntry(Base):
    """Model for food and calorie tracking."""

    __tablename__ = "food_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Food tracking data
    calories = Column(Float, nullable=False)
    meal_name = Column(String(255), nullable=True)  # Optional meal description
    meal_type = Column(String(50), nullable=True)  # breakfast, lunch, dinner, snack

    # Macronutrient tracking
    protein = Column(Float, nullable=True, default=0.0)  # grams
    carbs = Column(Float, nullable=True, default=0.0)  # grams
    fats = Column(Float, nullable=True, default=0.0)  # grams

    # Timestamps
    timestamp = Column(
        DateTime, nullable=False, index=True
    )  # When the meal was consumed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="food_entries")

    def __repr__(self):
        return f"<FoodEntry(id={self.id}, user_id={self.user_id}, calories={self.calories})>"

    def to_dict(self):
        """Convert food entry to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "calories": self.calories,
            "meal_name": self.meal_name,
            "meal_type": self.meal_type,
            "protein": self.protein,
            "carbs": self.carbs,
            "fats": self.fats,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
