from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class ReminderType(str, enum.Enum):
    EVENT = "EVENT"
    LEAVE_REQUEST = "LEAVE_REQUEST"
    BIRTHDAY = "BIRTHDAY"
    ANNIVERSARY = "ANNIVERSARY"
    DEADLINE = "DEADLINE"
    CUSTOM = "CUSTOM"


class ReminderStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReminderJob(BaseModel):
    """
    Reminder job model for scheduling and managing reminders.
    """
    __tablename__ = "reminder_jobs"
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reminder_type = Column(Enum(ReminderType), default=ReminderType.CUSTOM, nullable=False)
    
    # Target Information
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_email = Column(String(255), nullable=True)
    target_phone = Column(String(20), nullable=True)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Status
    status = Column(Enum(ReminderStatus), default=ReminderStatus.SCHEDULED, nullable=False)
    
    # Channels
    send_email = Column(Boolean, default=True, nullable=False)
    send_sms = Column(Boolean, default=False, nullable=False)
    send_push = Column(Boolean, default=False, nullable=False)
    
    # Processing Information
    processed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error Information
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    # Related Entity
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(100), nullable=True)  # daily, weekly, monthly, yearly
    recurrence_end_date = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)
    
    # Template Information
    email_template = Column(String(100), nullable=True)
    sms_template = Column(String(100), nullable=True)
    
    # Metadata
    priority = Column(String(20), default="NORMAL", nullable=False)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    
    # Relationships
    target_user = relationship("User", foreign_keys=[target_user_id])
    
    def __repr__(self):
        return f"<ReminderJob(id={self.id}, title={self.title}, status={self.status})>"
    
    def is_pending(self):
        return self.status == ReminderStatus.SCHEDULED and self.scheduled_at > func.now()
    
    def is_overdue(self):
        return self.status == ReminderStatus.SCHEDULED and self.scheduled_at <= func.now()
    
    def can_retry(self):
        return self.retry_count < self.max_retries and self.status == ReminderStatus.FAILED
    
    def schedule_next_run(self):
        if self.is_recurring and self.recurrence_pattern:
            # Logic to calculate next run time based on recurrence pattern
            # This would be implemented based on specific recurrence rules
            pass
