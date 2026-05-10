from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, Boolean, Numeric
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class EmailStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"
    UNSUBSCRIBED = "UNSUBSCRIBED"


class EmailProvider(str, enum.Enum):
    SENDGRID = "SENDGRID"
    AWS_SES = "AWS_SES"
    SMTP = "SMTP"
    MAILGUN = "MAILGUN"
    CUSTOM = "CUSTOM"


class EmailLog(BaseModel):
    """
    Email log model for tracking email communications.
    """
    __tablename__ = "email_logs"
    
    # Recipient Information
    to_email = Column(String(255), nullable=False, index=True)
    from_email = Column(String(255), nullable=False)
    cc_emails = Column(String(1000), nullable=True)  # Comma-separated
    bcc_emails = Column(String(1000), nullable=True)  # Comma-separated
    
    # Message Content
    subject = Column(String(500), nullable=False)
    html_content = Column(Text, nullable=True)
    text_content = Column(Text, nullable=True)
    template_name = Column(String(100), nullable=True)
    
    # Status and Tracking
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING, nullable=False)
    provider = Column(Enum(EmailProvider), default=EmailProvider.SMTP, nullable=False)
    external_id = Column(String(100), nullable=True)  # Provider's message ID
    
    # Engagement Tracking
    opened_at = Column(DateTime(timezone=True), nullable=True)
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery Information
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error Information
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    bounce_reason = Column(String(200), nullable=True)
    
    # Cost Information
    cost = Column(Numeric(10, 4), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Metadata
    campaign_name = Column(String(100), nullable=True)
    priority = Column(String(20), default="NORMAL", nullable=False)
    category = Column(String(50), nullable=True)  # notification, marketing, transactional
    
    # Related Entity
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Retry Information
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, to={self.to_email}, status={self.status})>"
    
    def is_delivered(self):
        return self.status in [EmailStatus.DELIVERED, EmailStatus.OPENED, EmailStatus.CLICKED]
    
    def is_failed(self):
        return self.status in [EmailStatus.FAILED, EmailStatus.BOUNCED]
    
    def is_opened(self):
        return self.status in [EmailStatus.OPENED, EmailStatus.CLICKED]
    
    def can_retry(self):
        return self.retry_count < self.max_retries and self.status == EmailStatus.FAILED
