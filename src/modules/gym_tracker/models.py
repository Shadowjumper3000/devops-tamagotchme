"""Gym tracker models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum

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
    name = Column(String, nullable=False)
    workout_type = Column(Enum(WorkoutType), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    calories_burned = Column(Float, nullable=True)
    distance_km = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship to strength exercises
    strength_exercises = relationship("StrengthExercise", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkoutEntry(id={self.id}, name={self.name}, type={self.workout_type})>"


class StrengthExercise(Base):
    """Model for strength training exercises within a workout."""

    __tablename__ = "strength_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workout_entries.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship back to workout
    workout = relationship("WorkoutEntry", back_populates="strength_exercises")

    @property
    def volume(self) -> float:
        """Calculate total volume (sets × reps × weight)."""
        return self.sets * self.reps * self.weight_kg

    def __repr__(self):
        return f"<StrengthExercise(id={self.id}, exercise={self.exercise_name}, volume={self.volume})>"
