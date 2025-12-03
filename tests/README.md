# Testing Guide

## Overview

Comprehensive unit tests for the Life Planner application covering all modules and business logic.

## Test Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── test_auth_service.py           # Authentication tests
├── test_water_tracker.py          # Water tracking module tests
├── test_food_tracker.py           # Food tracking module tests
├── test_gym_tracker.py            # Gym tracking module tests
├── test_health_calculator.py      # Pet health calculation logic tests
├── test_dashboard_service.py      # Dashboard orchestration tests
└── test_application.py            # Application integration tests
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_water_tracker.py
```

### Run specific test:
```bash
pytest tests/test_water_tracker.py::TestWaterTrackerService::test_log_water_success
```

### Run with verbose output:
```bash
pytest -v
```

### Run and show print statements:
```bash
pytest -s
```

## Test Coverage

### Modules Tested:

#### 1. **Water Tracker Service** (test_water_tracker.py)
- ✅ Log water intake
- ✅ Get daily/weekly summaries
- ✅ Update/delete entries
- ✅ Date range queries
- ✅ Empty state handling

#### 2. **Food Tracker Service** (test_food_tracker.py)
- ✅ Log food/meals
- ✅ Track calories
- ✅ Meal type filtering
- ✅ Daily/weekly summaries
- ✅ Update/delete entries
- ✅ Calorie breakdown by meal type

#### 3. **Gym Tracker Service** (test_gym_tracker.py)
- ✅ Log HIIT workouts
- ✅ Log cardio workouts
- ✅ Log strength training
- ✅ Daily/weekly summaries
- ✅ Workout type filtering
- ✅ Workout streaks
- ✅ Update/delete workouts

#### 4. **Authentication Service** (test_auth_service.py)
- ✅ User registration
- ✅ Login/logout
- ✅ Password hashing
- ✅ Duplicate email prevention
- ✅ User goal management
- ✅ Error handling

#### 5. **Health Calculator** (test_health_calculator.py) - **Core Business Logic**
- ✅ Perfect health calculation
- ✅ Component score calculations (water, food, exercise)
- ✅ Weight distribution (30-30-40)
- ✅ Status thresholds (thriving, healthy, okay, needs attention, critical)
- ✅ Edge cases (no activity, excessive/insufficient intake)
- ✅ Status messages
- ✅ Dehydration penalties

#### 6. **Dashboard Service** (test_dashboard_service.py) - **Main Orchestration**
- ✅ Complete dashboard data aggregation
- ✅ Pet health integration
- ✅ Progress tracking
- ✅ Weekly trends
- ✅ Multiple entries handling
- ✅ User not found handling
- ✅ Default date handling

#### 7. **Application** (test_application.py)
- ✅ Application initialization
- ✅ Component creation
- ✅ Initialization order (database first)
- ✅ Status reporting
- ✅ Health checks
- ✅ Shutdown

## Test Fixtures

### Database Fixtures:
- `db_engine` - In-memory SQLite database
- `db_session` - Database session for tests
- `sample_user` - Pre-created test user

### Utility Fixtures:
- `fixed_datetime` - Fixed datetime for consistent testing
- `test_config` - Test configuration

## Writing New Tests

### Example Test Structure:
```python
import pytest
from src.modules.your_module.service import YourService

class TestYourService:
    """Test suite for YourService."""

    @pytest.fixture
    def your_service(self, db_session):
        """Create service instance."""
        return YourService(db_session)

    def test_your_feature(self, your_service, sample_user):
        """Test description."""
        result = your_service.do_something(sample_user.id)
        assert result is not None
```

## Coverage Report

Generate and view coverage report:
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Continuous Integration

Tests are automatically run in CI/CD pipeline:
- **Dev branch**: All tests must pass
- **Prod branch**: All tests must pass before deployment

## Test Best Practices

1. ✅ Each test should be independent
2. ✅ Use fixtures for common setup
3. ✅ Test both success and failure cases
4. ✅ Use descriptive test names
5. ✅ Keep tests simple and focused
6. ✅ Mock external dependencies
7. ✅ Test edge cases
8. ✅ Aim for high coverage (>80%)

## Common Test Commands

```bash
# Fast test run (stop on first failure)
pytest -x

# Run tests in parallel (faster)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "water"

# Show slowest tests
pytest --durations=10
```

## Troubleshooting

### Import errors:
Make sure you're in the project root and Python path is set:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Database errors:
Tests use in-memory SQLite - no cleanup needed. Each test gets fresh database.

### Fixture not found:
Check that `conftest.py` is in the tests directory.

## Next Steps

- [ ] Add integration tests
- [ ] Add API endpoint tests
- [ ] Add performance tests
- [ ] Increase coverage to >90%
- [ ] Add mutation testing
