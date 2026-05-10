from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, Boolean, Numeric
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class SmsStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"


class SmsProvider(str, enum.Enum):
    TWILIO = "TWILIO"
    AWS_SNS = "AWS_SNS"
    SENDGRID = "SENDGRID"
    CUSTOM = "CUSTOM"


class SmsLog(BaseModel):
    """
    SMS log model for tracking SMS communications.
    """
    __tablename__ = "sms_logs"
    
    # Recipient Information
    phone_number = Column(String(20), nullable=False, index=True)
    country_code = Column(String(5), nullable=True)
    
    # Message Content
    message = Column(Text, nullable=False)
    template_name = Column(String(100), nullable=True)
    
    # Status and Tracking
    status = Column(Enum(SmsStatus), default=SmsStatus.PENDING, nullable=False)
    provider = Column(Enum(SmsProvider), default=SmsProvider.CUSTOM, nullable=False)
    external_id = Column(String(100), nullable=True)  # Provider's message ID
    
    # Cost Information
    cost = Column(Numeric(10, 4), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Delivery Information
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error Information
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    campaign_name = Column(String(100), nullable=True)
    priority = Column(String(20), default="NORMAL", nullable=False)
    
    # Related Entity
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Retry Information
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    def __repr__(self):
        return f"<SmsLog(id={self.id}, phone={self.phone_number}, status={self.status})>"
    
    def is_delivered(self):
        return self.status == SmsStatus.DELIVERED
    
    def is_failed(self):
        return self.status == SmsStatus.FAILED
    
    def can_retry(self):
        return self.retry_count < self.max_retries and self.status == SmsStatus.FAILED
