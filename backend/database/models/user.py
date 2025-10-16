# models/user.py
from beanie import Document
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserProfile(BaseModel):
    nationality: Optional[str] = None
    preferredLanguage: str = "en"
    frequentFlyer: Optional[str] = None

class User(Document):
    # Basic user information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = Field(default=None, index=True)
    phone: Optional[str] = Field(default=None, index=True)  # Make phone indexable for fast lookup
    preferred_name: Optional[str] = None  # nickname - optional
    profile: UserProfile = Field(default_factory=UserProfile)
    
    # OTP fields
    otp_code: Optional[str] = None
    otp_expires_at: Optional[datetime] = None
    otp_attempts: int = Field(default=0)
    verified_at: Optional[datetime] = None
    
    # Session management
    session_token: Optional[str] = Field(default=None, index=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "users"
        
    def is_otp_valid(self) -> bool:
        """Check if OTP is still valid (not expired)"""
        if not self.otp_expires_at:
            return False
        return datetime.utcnow() < self.otp_expires_at
        
    def can_request_otp(self) -> bool:
        """Check if user can request a new OTP (rate limiting)"""
        if not self.updated_at:
            return True
        # Allow new OTP request after 1 minute
        time_diff = datetime.utcnow() - self.updated_at
        return time_diff.total_seconds() > 60
