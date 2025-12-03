"""Water tracker data models."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ...core.database import Base


class WaterEntry(Base):
    """Model for water intake tracking."""

    __tablename__ = "water_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Water tracking data
    amount_ml = Column(Float, nullable=False)  # Amount in milliliters
    
    # Timestamps
    timestamp = Column(DateTime, nullable=False, index=True)  # When the water was consumed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="water_entries")

    def __repr__(self):
        return f"<WaterEntry(id={self.id}, user_id={self.user_id}, amount={self.amount_ml}ml)>"

    def to_dict(self):
        """Convert water entry to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount_ml": self.amount_ml,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
