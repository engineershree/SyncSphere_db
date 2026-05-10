from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class EventPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class EventType(str, enum.Enum):
    MEETING = "MEETING"
    HOLIDAY = "HOLIDAY"
    TRAINING = "TRAINING"
    CONFERENCE = "CONFERENCE"
    WORKSHOP = "WORKSHOP"
    SOCIAL = "SOCIAL"
    OTHER = "OTHER"


class Event(BaseModel):
    """
    Event model for scheduling and managing events.
    """
    __tablename__ = "events"
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(Enum(EventType), default=EventType.OTHER, nullable=False)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    priority = Column(Enum(EventPriority), default=EventPriority.MEDIUM, nullable=False)
    
    # Timing
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    all_day = Column(Boolean, default=False, nullable=False)
    
    # Location
    location = Column(String(500), nullable=True)
    virtual_meeting_url = Column(String(500), nullable=True)
    virtual_meeting_id = Column(String(100), nullable=True)
    
    # Attendees
    max_attendees = Column(Integer, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    requires_registration = Column(Boolean, default=False, nullable=False)
    
    # Creator and Management
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Reminders
    reminder_enabled = Column(Boolean, default=True, nullable=False)
    reminder_minutes_before = Column(Integer, default=15, nullable=False)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)  # daily, weekly, monthly, yearly
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    external_calendar_id = Column(String(100), nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="events_created", foreign_keys=[creator_id])
    organizer = relationship("User", foreign_keys=[organizer_id])
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, status={self.status})>"
    
    @property
    def duration_minutes(self):
        if self.start_datetime and self.end_datetime:
            return int((self.end_datetime - self.start_datetime).total_seconds() / 60)
        return None
    
    def is_upcoming(self):
        return self.start_datetime > func.now() and self.status == EventStatus.PUBLISHED
    
    def is_ongoing(self):
        now = func.now()
        return self.start_datetime <= now <= self.end_datetime and self.status == EventStatus.PUBLISHED
