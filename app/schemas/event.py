from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

from app.models.event import EventStatus, EventPriority, EventType


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_type: EventType = EventType.OTHER
    status: EventStatus = EventStatus.DRAFT
    priority: EventPriority = EventPriority.MEDIUM
    start_datetime: datetime
    end_datetime: datetime
    timezone: str = "UTC"
    all_day: bool = False
    location: Optional[str] = None
    virtual_meeting_url: Optional[str] = None
    virtual_meeting_id: Optional[str] = None
    max_attendees: Optional[int] = None
    is_public: bool = False
    requires_registration: bool = False
    organizer_id: Optional[int] = None
    reminder_enabled: bool = True
    reminder_minutes_before: int = 15
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None
    recurrence_end_date: Optional[datetime] = None
    tags: Optional[str] = None
    external_calendar_id: Optional[str] = None
    
    @validator('end_datetime')
    def validate_end_datetime(cls, v, values):
        if 'start_datetime' in values and v <= values['start_datetime']:
            raise ValueError('End datetime must be after start datetime')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventResponse(EventBase):
    id: int
    uuid: str
    creator_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
