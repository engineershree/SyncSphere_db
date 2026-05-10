from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    uuid: str
    status: str
    is_email_verified: bool
    is_phone_verified: bool
    refresh_token: Optional[str] = None
    refresh_token_expires_at: Optional[datetime] = None
    refresh_token_jti: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None
    timezone: str
    language: str
    email_notifications: bool
    sms_notifications: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
