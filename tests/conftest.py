"""Pytest configuration and fixtures."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.core.database import Base


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    
    # Import models to ensure they're registered
    from src.modules.auth.models import User
    from src.modules.food_tracker.models import FoodEntry
    from src.modules.water_tracker.models import WaterEntry
    from src.modules.gym_tracker.models import WorkoutEntry
    
    yield session
    session.close()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    from src.modules.auth.models import User
    from src.modules.auth.utils import PasswordHasher
    
    hasher = PasswordHasher()
    user = User(
        email="test@example.com",
        password_hash=hasher.hash_password("testpassword"),
        daily_water_goal=2000,
        daily_calorie_goal=2000,
        weekly_exercise_goal=3
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def fixed_datetime():
    """Return a fixed datetime for consistent testing."""
    return datetime(2025, 12, 3, 12, 0, 0)
