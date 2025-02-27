# app/models/auth.py
from typing import Optional
from pydantic import BaseModel, EmailStr, validator
import re

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    phone: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    
    @validator('pan_number')
    def validate_pan(cls, v):
        if v is not None:
            pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
            if not re.match(pattern, v):
                raise ValueError('Invalid PAN number format')
        return v
    
    @validator('aadhar_number')
    def validate_aadhar(cls, v):
        if v is not None:
            if not re.match(r'^\d{12}$', v):
                raise ValueError('Aadhar must be 12 digits')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class UserProfile(UserBase):
    id: int
    phone: Optional[str] = None
    pan_number: Optional[str] = None
    aadhar_number: Optional[str] = None
    profile_image_url: Optional[str] = None
    is_verified: bool
    
    class Config:
        orm_mode = True