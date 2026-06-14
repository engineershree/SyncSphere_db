from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

from app.models.user import UserRole, UserStatus


class UserBase(BaseModel):
    id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[int] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None


class UserCreate(UserBase):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    uuid: str
    email: EmailStr
    is_email_verified: bool
    is_phone_verified: bool
    last_login_at: Optional[datetime] = None
    password_changed_at: datetime
    failed_login_attempts: str
    locked_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
