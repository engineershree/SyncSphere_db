from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.models.leave_request import LeaveType, LeaveStatus


class LeaveRequestBase(BaseModel):
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    return_date: Optional[datetime] = None
    total_days: Decimal
    working_days: Decimal
    reason: str
    employee_comments: Optional[str] = None
    attachment_url: Optional[str] = None
    balance_before: Optional[Decimal] = None
    balance_after: Optional[Decimal] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_half_day: bool = False
    half_day_type: Optional[str] = None
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v
    
    @validator('total_days', 'working_days')
    def validate_days(cls, v):
        if v <= 0:
            raise ValueError('Days must be greater than 0')
        return v


class LeaveRequestCreate(LeaveRequestBase):
    pass


class LeaveRequestUpdate(LeaveRequestBase):
    status: Optional[LeaveStatus] = None
    approver_comments: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None


class LeaveRequestResponse(LeaveRequestBase):
    id: int
    uuid: str
    status: LeaveStatus
    user_id: int
    approver_id: Optional[int] = None
    approver_comments: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
