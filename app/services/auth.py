# app/services/auth.py
from datetime import datetime, timedelta
import secrets
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import EmailStr

from app.database.models import User, AuthToken
from app.models.auth import UserCreate
from app.utils.security import get_password_hash, verify_password
from app.config import settings

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by email.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get a user by ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Create a new user.
    """
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        full_name=user_in.full_name,
        phone=user_in.phone,
        pan_number=user_in.pan_number,
        aadhar_number=user_in.aadhar_number,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)
    
    return user

def generate_verification_token(db: Session, user_id: int) -> str:
    """
    Generate a token for email verification.
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=1)
    
    db_token = AuthToken(
        user_id=user_id,
        token=token,
        token_type="verification",
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def send_verification_email(email: str, user_id: int, db: Session) -> None:
    """
    Send verification email to user.
    In a real application, this would use an email service.
    """
    token = generate_verification_token(db, user_id)
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    # In a real application, send an actual email
    print(f"Sending verification email to {email}")
    print(f"Verification URL: {verification_url}")

def verify_user_email(db: Session, token: str) -> bool:
    """
    Verify user email with token.
    """
    db_token = db.query(AuthToken).filter(
        AuthToken.token == token,
        AuthToken.token_type == "verification",
        AuthToken.expires_at > datetime.now()
    ).first()
    
    if not db_token:
        return False
    
    user = get_user_by_id(db, db_token.user_id)
    if not user:
        return False
    
    user.is_verified = True
    db.delete(db_token)
    db.commit()
    
    return True

def generate_password_reset_token(db: Session, user_id: int) -> str:
    """
    Generate a token for password reset.
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)
    
    db_token = AuthToken(
        user_id=user_id,
        token=token,
        token_type="reset_password",
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def reset_password_request(email: str, db: Session) -> None:
    """
    Process password reset request.
    In a real application, this would send an email.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return
    
    token = generate_password_reset_token(db, user.id)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    # In a real application, send an actual email
    print(f"Sending password reset email to {email}")
    print(f"Reset URL: {reset_url}")

def reset_password_confirm(db: Session, token: str, new_password: str) -> bool:
    """
    Confirm password reset with token and set new password.
    """
    db_token = db.query(AuthToken).filter(
        AuthToken.token == token,
        AuthToken.token_type == "reset_password",
        AuthToken.expires_at > datetime.now()
    ).first()
    
    if not db_token:
        return False
    
    user = get_user_by_id(db, db_token.user_id)
    if not user:
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.delete(db_token)
    db.commit()
    
    return True

def update_user_profile(db: Session, user_id: int, profile_data: dict) -> User:
    """
    Update user profile data.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update only the fields that are provided
    for field, value in profile_data.items():
        if hasattr(user, field) and field != "id" and field != "password_hash":
            setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
    """
    Change user password.
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    if not verify_password(current_password, user.password_hash):
        return False
    
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return True