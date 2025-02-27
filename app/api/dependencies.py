# app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import User
from app.utils.security import get_current_user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    return current_user