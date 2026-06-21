from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_token
from app.models.user import User
from app.models.blacklisted_token import BlacklistedToken

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user. Rejects blacklisted (logged-out) tokens.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    raw_token = credentials.credentials

    # Reject tokens that have been explicitly logged out
    is_blacklisted = db.query(BlacklistedToken).filter(
        BlacklistedToken.token == raw_token
    ).first()
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = verify_token(raw_token)
    if user_id is None:
        print("get_current_user: user_id is None (verify_token failed)")
        raise credentials_exception

    try:
        user_id_int = int(user_id)
    except ValueError:
        print(f"get_current_user: failed to cast user_id '{user_id}' to int")
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id_int, User.is_deleted == False).first()
    if user is None:
        print(f"get_current_user: user not found in DB for id {user_id_int}")
        raise credentials_exception

    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current admin user.
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_hr_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current HR user.
    """
    if not current_user.is_hr():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    db: Session = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None.
    """
    if credentials is None:
        return None
    
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        return None
    
    try:
        user_id_int = int(user_id)
    except ValueError:
        return None
    
    user = db.query(User).filter(User.id == user_id_int, User.is_deleted == False).first()
    if user is None or user.status != "ACTIVE":
        return None
    
    return user
