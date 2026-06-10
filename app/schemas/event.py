from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

from app.models.event import EventStatus, EventPriority, EventType


class EventCreate(BaseModel):
    """Schema for creating a new event - minimal required fields only."""
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    status: EventStatus = EventStatus.DRAFT
    priority: EventPriority = EventPriority.MEDIUM
    start_datetime: datetime
    timezone: str = "UTC"
    all_day: bool = False
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    is_public: bool = False
    requires_registration: bool = False
    organizer_id: Optional[int] = None
    reminder_enabled: bool = True
    external_calendar_id: Optional[str] = None


class EventUpdate(BaseModel):
    """Schema for updating an existing event."""
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    priority: Optional[EventPriority] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    timezone: Optional[str] = None
    all_day: Optional[bool] = None
    location: Optional[str] = None
    virtual_meeting_url: Optional[str] = None
    virtual_meeting_id: Optional[str] = None
    max_attendees: Optional[int] = None
    is_public: Optional[bool] = None
    requires_registration: Optional[bool] = None
    organizer_id: Optional[int] = None
    reminder_enabled: Optional[bool] = None
    reminder_minutes_before: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    tags: Optional[str] = None
    external_calendar_id: Optional[str] = None


class EventResponse(BaseModel):
    """Schema for event response."""
    id: int
    uuid: str
    title: str
    description: Optional[str] = None
    event_type: EventType
    status: EventStatus
    priority: EventPriority
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    timezone: str
    all_day: bool
    location: Optional[str] = None
    max_attendees: Optional[int] = None
    is_public: bool
    requires_registration: bool
    organizer_id: Optional[int] = None
    creator_id: int
    reminder_enabled: bool
    external_calendar_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
