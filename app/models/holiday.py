from sqlalchemy import Column, String, Enum, DateTime, Boolean, Text
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class HolidayType(str, enum.Enum):
    NATIONAL = "NATIONAL"
    RELIGIOUS = "RELIGIOUS"
    COMPANY = "COMPANY"
    CUSTOM = "CUSTOM"


class Holiday(BaseModel):
    """
    Holiday model for managing company and national holidays.
    """
    __tablename__ = "holidays"
    
    # Basic Information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    holiday_type = Column(Enum(HolidayType), default=HolidayType.NATIONAL, nullable=False)
    
    # Date Information
    date = Column(DateTime(timezone=True), nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Additional Information
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Holiday(id={self.id}, name={self.name}, date={self.date})>"
    
    def is_today(self):
        today = func.now().date()
        return self.date.date() == today
