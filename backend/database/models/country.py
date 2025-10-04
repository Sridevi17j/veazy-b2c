# models/country.py
from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime

class Country(Document):
    code: str = Field(index=True)  # ISO 3166-1 alpha-3
    name: str = Field(index=True)
    official_name: Optional[str] = None
    supported_visas: List[str] = Field(default_factory=list)
    currency: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "countries"
