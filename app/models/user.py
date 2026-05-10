from sqlalchemy import Column, String, Enum, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    EVENT_MANAGER = "EVENT_MANAGER"
    HR_MANAGER = "HR_MANAGER"
    EMPLOYEE = "EMPLOYEE"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"
    PENDING = "PENDING"


class User(BaseModel):
    """
    User model with authentication and role-based access.
    """
    __tablename__ = "users"
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_phone_verified = Column(Boolean, default=False, nullable=False)
    
    # Role and Status
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING, nullable=False)
    
    # Profile
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    department = Column(String(100), nullable=True)
    job_title = Column(String(100), nullable=True)
    employee_id = Column(String(50), unique=True, index=True, nullable=True)
    
    # Preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    
    # Security
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    failed_login_attempts = Column(String(10), default="0", nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    events_created = relationship("Event", back_populates="creator", foreign_keys="Event.creator_id")
    leave_requests = relationship("LeaveRequest", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def is_active(self):
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    def is_admin(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]
    
    def is_hr(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.HR_MANAGER]
    
    def can_manage_events(self):
        return self.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.EVENT_MANAGER]
