# app/api/routes/auth.py
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.db import get_db
from app.database.models import User
from app.models.auth import UserCreate, UserLogin, Token, UserProfile
from app.services.auth import (
    authenticate_user,
    create_user,
    get_user_by_email,
    send_verification_email,
    verify_user_email,
    reset_password_request,
    reset_password_confirm,
    update_user_profile,
    change_password,
)
from app.utils.security import create_access_token, create_refresh_token
from app.config import settings

router = APIRouter()

@router.post("/register", response_model=dict)
def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = create_user(db=db, user_in=user_in)
    # Send verification email in background
    background_tasks.add_task(send_verification_email, user.email, user.id, db)
    
    return {
        "message": "User registered successfully. Please check your email to verify your account.",
        "email": user.email
    }


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first.",
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=Token)
def refresh_token(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh token.
    """
    # Logic to validate refresh token and issue new tokens
    # This would be implemented in the auth service
    pass


@router.post("/verify/{token}")
def verify_email(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify user email with token.
    """
    if verify_user_email(db, token):
        return {"message": "Email verified successfully. You can now login."}
    raise HTTPException(
        status_code=400,
        detail="Invalid or expired verification token",
    )


@router.post("/reset-password")
def reset_password(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Password recovery by email.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        # Don't reveal that the user doesn't exist
        return {"message": "If this email exists in our system, a password reset link has been sent."}
    
    background_tasks.add_task(reset_password_request, email, db)
    return {"message": "If this email exists in our system, a password reset link has been sent."}


@router.post("/reset-password-confirm/{token}")
def reset_password_confirmation(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Reset password with token.
    """
    if reset_password_confirm(db, token, new_password):
        return {"message": "Password reset successful. You can now login with your new password."}
    raise HTTPException(
        status_code=400,
        detail="Invalid or expired password reset token",
    )


@router.get("/profile", response_model=UserProfile)
def get_user_profile(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get current user profile.
    """
    return current_user


@router.put("/profile", response_model=UserProfile)
def update_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current user profile.
    """
    updated_user = update_user_profile(db, current_user.id, profile_data)
    return updated_user


@router.post("/change-password")
def update_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Change user password.
    """
    if change_password(db, current_user.id, current_password, new_password):
        return {"message": "Password updated successfully"}
    raise HTTPException(
        status_code=400,
        detail="Incorrect current password",
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Logout user (revoke token).
    """
    # Implement token revocation if needed
    return {"message": "Successfully logged out"}