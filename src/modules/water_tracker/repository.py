"""Repository for water tracker operations."""

import logging
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from ...shared.database_interface import BaseRepository
from .models import WaterEntry

logger = logging.getLogger(__name__)


class WaterRepository(BaseRepository):
    """Repository for water tracker operations."""

    def __init__(self, db_session: Session):
        """Initialize with WaterEntry as the primary model."""
        super().__init__(db_session, WaterEntry)

    def get_entries_by_user_and_date(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[WaterEntry]:
        """
        Get water entries for a user within a date range.
        
        Args:
            user_id: User's ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of water entries
        """
        try:
            return self.db_session.query(WaterEntry).filter(
                WaterEntry.user_id == user_id,
                WaterEntry.timestamp >= start_date,
                WaterEntry.timestamp <= end_date
            ).order_by(WaterEntry.timestamp.desc()).all()
        except Exception as e:
            logger.error(f"Failed to get entries: {e}")
            return []
