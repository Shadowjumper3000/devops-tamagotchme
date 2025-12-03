"""Gym tracker models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
import json

from ...core.database import Base


class WorkoutType(enum.Enum):
    """Workout type enumeration."""
    CARDIO = "cardio"
    STRENGTH = "strength"
    FLEXIBILITY = "flexibility"
    SPORTS = "sports"
    OTHER = "other"


class WorkoutEntry(Base):
    """Model for workout entries."""

    __tablename__ = "workout_entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Morning Run", "Bench Press"
    workout_type = Column(Enum(WorkoutType), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)  # For cardio
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to strength exercises
    strength_exercises = relationship("StrengthExercise", back_populates="workout", cascade="all, delete-orphan")


class StrengthExercise(Base):
    """Model for strength training exercises within a workout."""

    __tablename__ = "strength_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, nullable=False)
    exercise_name = Column(String, nullable=False)  # e.g., "Bench Press", "Squat"
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="workout_entries")

    # Relationship
    workout = relationship("WorkoutEntry", back_populates="strength_exercises")
    def __repr__(self):
        return f"<WorkoutEntry(id={self.id}, user_id={self.user_id}, type={self.workout_type})>"

    @property
    def volume(self) -> float:
        """Calculate total volume (sets × reps × weight)."""
        return self.sets * self.reps * self.weight_kg
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
