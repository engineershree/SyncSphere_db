from sqlalchemy import Column, String, Enum, DateTime, Text, Integer, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import BaseModel


class LeaveType(str, enum.Enum):
    SICK = "SICK"
    VACATION = "VACATION"
    PERSONAL = "PERSONAL"
    MATERNITY = "MATERNITY"
    PATERNITY = "PATERNITY"
    COMPENSATORY = "COMPENSATORY"
    UNPAID = "UNPAID"
    BEREAVEMENT = "BEREAVEMENT"


class LeaveStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"
    ON_HOLD = "ON_HOLD"


class LeaveRequest(BaseModel):
    """
    Leave request model for employee leave management.
    """
    __tablename__ = "leave_requests"
    
    # Basic Information
    leave_type = Column(Enum(LeaveType), nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    
    # Duration
    total_days = Column(Numeric(3, 1), nullable=False)  # Can handle half days
    working_days = Column(Numeric(3, 1), nullable=False)
    
    # Reason and Comments
    reason = Column(Text, nullable=False)
    employee_comments = Column(Text, nullable=True)
    approver_comments = Column(Text, nullable=True)
    
    # User Information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Attachments
    attachment_url = Column(String(500), nullable=True)
    
    # Leave Balance
    balance_before = Column(Numeric(3, 1), nullable=True)
    balance_after = Column(Numeric(3, 1), nullable=True)
    
    # Emergency Contact
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Workflow
    is_half_day = Column(Boolean, default=False, nullable=False)
    half_day_type = Column(String(20), nullable=True)  # FIRST_HALF, SECOND_HALF
    
    # Approval Dates
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="leave_requests", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])
    
    def __repr__(self):
        return f"<LeaveRequest(id={self.id}, type={self.leave_type}, status={self.status})>"
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    
    def is_approved(self):
        return self.status == LeaveStatus.APPROVED
    
    def is_pending(self):
        return self.status == LeaveStatus.PENDING
    
    def can_be_cancelled(self):
        return self.status in [LeaveStatus.PENDING, LeaveStatus.APPROVED] and self.start_date > func.now()
