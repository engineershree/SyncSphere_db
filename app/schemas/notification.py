from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

from app.models.notification import NotificationType, NotificationChannel


class NotificationBase(BaseModel):
    title: str
    message: str
    notification_type: NotificationType = NotificationType.INFO
    channels: str  # Comma-separated channels
    scheduled_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    priority: str = "MEDIUM"
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    
    @validator('channels')
    def validate_channels(cls, v):
        valid_channels = [channel.value for channel in NotificationChannel]
        channel_list = [c.strip() for c in v.split(',')]
        for channel in channel_list:
            if channel not in valid_channels:
                raise ValueError(f'Invalid channel: {channel}. Valid channels: {valid_channels}')
        return v


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: int
    uuid: str
    user_id: int
    is_read: bool
    read_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    email_sent: bool
    sms_sent: bool
    push_sent: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
