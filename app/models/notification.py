from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class NotificationType(str, enum.Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    LEAVE_APPROVAL = "LEAVE_APPROVAL"
    EVENT_REMINDER = "EVENT_REMINDER"
    SYSTEM_UPDATE = "SYSTEM_UPDATE"


class NotificationChannel(str, enum.Enum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"


class Notification(BaseModel):
    """
    Notification model for managing user notifications.
    """
    __tablename__ = "notifications"
    
    # Basic Information
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), default=NotificationType.INFO, nullable=False)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Channels
    channels = Column(String(100), nullable=False)  # Comma-separated channels
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    action_url = Column(String(500), nullable=True)
    action_text = Column(String(100), nullable=True)
    priority = Column(String(20), default="MEDIUM", nullable=False)
    
    # Related Entity
    related_entity_type = Column(String(50), nullable=True)  # event, leave_request, etc.
    related_entity_id = Column(Integer, nullable=True)
    
    # Delivery Status
    email_sent = Column(Boolean, default=False, nullable=False)
    sms_sent = Column(Boolean, default=False, nullable=False)
    push_sent = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title}, type={self.notification_type})>"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = func.now()
    
    def is_unread(self):
        return not self.is_read
    
    def has_channel(self, channel: NotificationChannel):
        return channel.value in self.channels.split(',') if self.channels else False
