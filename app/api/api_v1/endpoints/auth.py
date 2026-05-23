from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.core.security import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.core.deps import get_current_user
from app.models.user import User, UserStatus
from app.schemas.auth import Token, UserCreate, UserLogin, UserResponse, AuthResponse
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
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    
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
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return current_user
