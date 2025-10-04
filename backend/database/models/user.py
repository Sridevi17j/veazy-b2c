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
    email: EmailStr = Field(index=True)
    phone: Optional[str] = None
    preferred_name: Optional[str] = None
    profile: UserProfile = Field(default_factory=UserProfile)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "users"
