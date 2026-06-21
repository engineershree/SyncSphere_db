from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Any
from datetime import datetime, timedelta
import random
from jose import JWTError, jwt

from app.db.session import get_db
from app.core.security import (
    create_access_token, create_refresh_token,
    get_password_hash, verify_password, verify_token
)
from app.core.config import settings
from app.core.deps import get_current_user
from app.models.user import User, UserStatus
from app.models.blacklisted_token import BlacklistedToken
from app.schemas.auth import (
    Token, UserCreate, UserLogin, UserResponse, AuthResponse,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=AuthResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    logger.debug(f"Attempting to register new user with email: {user_data.email}")
    
    # Check if user already exists
    if user_data.phone:
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.phone == user_data.phone)
        ).first()
    else:
        existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        logger.warning(f"Registration failed: User with email {user_data.email} or phone {user_data.phone} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        status=UserStatus.ACTIVE
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Successfully registered new user: {user.email} (Role: {user.role})")
    
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
) -> Any:
    """
    Authenticate user and return access token.
    """
    logger.debug(f"Login attempt for email: {user_credentials.email}")
    
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        logger.warning(f"Login failed: Incorrect email or password for {user_credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.status != UserStatus.ACTIVE:
        logger.warning(f"Login failed: Account {user_credentials.email} is not active (Status: {user.status})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    # Create access token
    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)
    
    logger.info(f"Successful login for user: {user.email}")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Logout the current user by blacklisting their access token.
    After calling this endpoint, the token will be rejected on all protected routes.
    """
    raw_token = credentials.credentials

    # Decode token to get expiry (for record-keeping)
    try:
        payload = jwt.decode(
            raw_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        exp_timestamp = payload.get("exp")
        expires_at = datetime.utcfromtimestamp(exp_timestamp) if exp_timestamp else datetime.utcnow()
    except JWTError:
        expires_at = datetime.utcnow()

    # Check not already blacklisted (idempotent)
    already_blacklisted = db.query(BlacklistedToken).filter(
        BlacklistedToken.token == raw_token
    ).first()

    if not already_blacklisted:
        blacklisted = BlacklistedToken(token=raw_token, expires_at=expires_at)
        db.add(blacklisted)
        db.commit()

    logger.info(f"User {current_user.email} logged out successfully")

    return {
        "message": "Logged out successfully",
        "user": current_user.email
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Any:
    """
    Issue a new access token using a valid refresh token.
    """
    raw_token = credentials.credentials

    try:
        payload = jwt.decode(
            raw_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a refresh token"
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == int(user_id), User.is_deleted == False).first()
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access_token = create_access_token(subject=user.id)

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/forgot-password")
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Send OTP code for password reset.
    """
    user = db.query(User).filter(User.email == request_data.email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    # Generate 6-digit OTP
    otp_code = f"{random.randint(100000, 999999)}"
    user.otp = otp_code
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()
    
    # Log in terminal (requested: "and also check the terminal")
    logger.info(f"🔑 RESET PASSWORD OTP FOR {user.email}: {otp_code}")
    print(f"\n========================================\n🔑 RESET PASSWORD OTP FOR {user.email}: {otp_code}\n========================================\n")
    
    # Optional: Send via SMTP (catch failure to prevent 500 error in case SMTP is unconfigured)
    if settings.SMTP_HOST and settings.SMTP_USERNAME:
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(f"Your SyncSphere password reset OTP code is: {otp_code}. It is valid for 10 minutes.")
            msg['Subject'] = "SyncSphere Password Reset OTP"
            msg['From'] = settings.EMAILS_FROM_EMAIL or settings.SMTP_USERNAME
            msg['To'] = user.email
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"OTP email sent to {user.email}")
        except Exception as e:
            logger.warning(f"Failed to send OTP email via SMTP: {e}")

    # Return OTP directly in response for development convenience
    return {
        "message": "OTP code has been generated and logged to the server terminal",
        "otp": otp_code  # Exposing in dev mode so testing Swagger UI works instantly
    }


@router.post("/verify-otp")
async def verify_otp(
    request_data: VerifyOTPRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify if the sent OTP is correct and not expired.
    """
    user = db.query(User).filter(User.email == request_data.email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    if not user.otp or user.otp != request_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
        
    if user.otp_expires_at and user.otp_expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired"
        )
        
    return {"message": "OTP code verified successfully"}


@router.post("/reset-password")
async def reset_password(
    request_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify OTP and reset password to the new password.
    """
    user = db.query(User).filter(User.email == request_data.email, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
        
    if not user.otp or user.otp != request_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
        
    if user.otp_expires_at and user.otp_expires_at.replace(tzinfo=None) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired"
        )
        
    # Reset password
    user.password_hash = get_password_hash(request_data.new_password)
    user.otp = None
    user.otp_expires_at = None
    user.password_changed_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Password reset successfully for user: {user.email}")
    return {"message": "Password reset successfully"}
