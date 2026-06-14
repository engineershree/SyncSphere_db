from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[int] = None
    role: UserRole = UserRole.EMPLOYEE

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must contain at least one special character (e.g., @$!%*?&)')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v


class UserResponse(UserBase):
    id: int
    uuid: str
    status: str
    is_email_verified: bool
    is_phone_verified: bool
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
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

    @validator('email')
    def email_to_lower(cls, v):
        return v.lower() if v else v

    @validator('new_password')
    def validate_new_password(cls, v):
        import re
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[@$!%*?&]', v):
            raise ValueError('Password must contain at least one special character (e.g., @$!%*?&)')
        return v
