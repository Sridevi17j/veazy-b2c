# models/country.py
from beanie import Document
from pydantic import Field
from typing import Optional

class Country(Document):
    code: str = Field(index=True)  # ISO 3166-1 alpha-3
    name: str = Field(index=True)
    official_name: Optional[str] = None
    currency: Optional[str] = None
    
    class Settings:
        collection = "countries"
