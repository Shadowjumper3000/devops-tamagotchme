"""Gym tracker data models."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
import enum
import json

from ...core.database import Base


class WorkoutType(enum.Enum):
    """Enum for workout types."""
    HIIT = "HIIT"
    CARDIO = "Cardio"


class WorkoutEntry(Base):
    """Model for workout tracking."""

    __tablename__ = "workout_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Workout type
    workout_type = Column(String(20), nullable=False)  # HIIT or Cardio
    
    # HIIT specific data (stored as JSON)
    # Format: [{"exercise": "Push-ups", "reps": 20, "weight": 0}, ...]
    exercises = Column(Text, nullable=True)  # JSON string for HIIT exercises
    
    # Cardio specific data
    exercise_name = Column(String(255), nullable=True)  # For Cardio: running, cycling, etc.
    duration_minutes = Column(Float, nullable=True)  # For Cardio: duration in minutes
    
    # Optional general fields
    notes = Column(Text, nullable=True)
    intensity = Column(String(20), nullable=True)  # low, medium, high
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)  # When the workout was performed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="workout_entries")

    def __repr__(self):
        return f"<WorkoutEntry(id={self.id}, user_id={self.user_id}, type={self.workout_type})>"

    def get_exercises_list(self):
        """Parse exercises JSON string to list."""
        if self.exercises:
            try:
                return json.loads(self.exercises)
            except json.JSONDecodeError:
                return []
        return []

    def set_exercises_list(self, exercises_list):
        """Convert exercises list to JSON string."""
        if exercises_list:
            self.exercises = json.dumps(exercises_list)
        else:
            self.exercises = None

    def to_dict(self):
        """Convert workout entry to dictionary."""
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "workout_type": self.workout_type,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "notes": self.notes,
            "intensity": self.intensity,
        }
        
        if self.workout_type == "HIIT":
            result["exercises"] = self.get_exercises_list()
        elif self.workout_type == "Cardio":
            result["exercise_name"] = self.exercise_name
            result["duration_minutes"] = self.duration_minutes
        
        return result
