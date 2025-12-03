"""Unit tests for Water Tracker Service."""

import pytest
from datetime import datetime, timedelta
from src.modules.water_tracker.service import WaterTrackerService


class TestWaterTrackerService:
    """Test suite for WaterTrackerService."""

    @pytest.fixture
    def water_service(self, db_session):
        """Create a water tracker service instance."""
        return WaterTrackerService(db_session)

    def test_log_water_success(self, water_service, sample_user):
        """Test logging water intake successfully."""
        result = water_service.log_water(
            user_id=sample_user.id,
            amount_ml=500.0
        )
        
        assert result is not None
        assert result["user_id"] == sample_user.id
        assert result["amount_ml"] == 500.0
        assert "timestamp" in result

    def test_log_water_custom_timestamp(self, water_service, sample_user, fixed_datetime):
        """Test logging water with custom timestamp."""
        result = water_service.log_water(
            user_id=sample_user.id,
            amount_ml=300.0,
            timestamp=fixed_datetime
        )
        
        assert result["amount_ml"] == 300.0
        assert result["timestamp"] == fixed_datetime.isoformat()

    def test_get_daily_summary(self, water_service, sample_user, fixed_datetime):
        """Test getting daily water summary."""
        # Log multiple water entries
        water_service.log_water(sample_user.id, 500.0, fixed_datetime)
        water_service.log_water(sample_user.id, 300.0, fixed_datetime)
        water_service.log_water(sample_user.id, 200.0, fixed_datetime)
        
        summary = water_service.get_daily_summary(sample_user.id, fixed_datetime)
        
        assert summary["total_ml"] == 1000.0
        assert summary["entry_count"] == 3

    def test_get_weekly_summary(self, water_service, sample_user, fixed_datetime):
        """Test getting weekly water summary."""
        # Log entries across multiple days
        for i in range(7):
            date = fixed_datetime - timedelta(days=i)
            water_service.log_water(sample_user.id, 500.0, date)
        
        summary = water_service.get_weekly_summary(sample_user.id, fixed_datetime)
        
        assert summary["total_ml"] == 3500.0
        assert summary["entry_count"] == 7
        assert summary["average_daily_ml"] == 500.0

    def test_update_entry(self, water_service, sample_user):
        """Test updating a water entry."""
        entry = water_service.log_water(sample_user.id, 500.0)
        entry_id = entry["id"]
        
        updated = water_service.update_entry(
            entry_id=entry_id,
            amount_ml=600.0
        )
        
        assert updated["amount_ml"] == 600.0

    def test_delete_entry(self, water_service, sample_user):
        """Test deleting a water entry."""
        entry = water_service.log_water(sample_user.id, 500.0)
        entry_id = entry["id"]
        
        result = water_service.delete_entry(entry_id)
        
        assert result is True

    def test_get_entries_by_date_range(self, water_service, sample_user, fixed_datetime):
        """Test getting entries by date range."""
        start_date = fixed_datetime
        end_date = fixed_datetime + timedelta(days=2)
        
        water_service.log_water(sample_user.id, 500.0, start_date)
        water_service.log_water(sample_user.id, 600.0, start_date + timedelta(days=1))
        water_service.log_water(sample_user.id, 700.0, end_date)
        
        entries = water_service.get_entries_by_date_range(
            sample_user.id, 
            start_date, 
            end_date
        )
        
        assert len(entries) == 3

    def test_daily_summary_empty(self, water_service, sample_user, fixed_datetime):
        """Test daily summary with no entries."""
        summary = water_service.get_daily_summary(sample_user.id, fixed_datetime)
        
        assert summary["total_ml"] == 0
        assert summary["entry_count"] == 0
