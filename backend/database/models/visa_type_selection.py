# models/visa_type_selection.py
from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import pymongo

class MatchWeights(BaseModel):
    purpose_exact: float = 1.0
    purpose_partial: float = 0.7
    traveller_count: float = 0.9

class SelectionCriteria(BaseModel):
    purpose: List[str]
    max_days: int
    min_travellers: int = 1
    max_travellers: Optional[int] = None

class VisaDetails(BaseModel):
    stay_duration: str  # "Up to 30 days"
    validity_period: str  # "30 days" 
    entry_type: str  # "Single Entry Only"
    processing_time: str  # "3-5 business days"
    fee_range: str  # "$25-50"
    description: Optional[str] = None

class DocumentRequirement(BaseModel):
    name: str  # "Passport"
    description: str  # "A valid passport with minimum 6 months validity..."
    required: bool = True
    category: str  # "identity", "travel", "financial", "supporting"
    notes: Optional[str] = None

class ProcessStep(BaseModel):
    step_number: int
    title: str  # "Application Processing"
    description: str
    estimated_time: str  # "1-2 days"

class VisaTypeRule(BaseModel):
    visa_type: str
    visa_code: str
    priority: Optional[int] = None
    criteria: SelectionCriteria
    match_weights: MatchWeights = Field(default_factory=MatchWeights)
    # Enhanced information
    visa_details: Optional[VisaDetails] = None
    document_requirements: Optional[List[DocumentRequirement]] = None
    approval_process: Optional[List[ProcessStep]] = None

class VisaTypeSelection(Document):
    country_code: Indexed(str, index_type=pymongo.ASCENDING)
    country_name: Indexed(str, index_type=pymongo.TEXT)
    rules: List[VisaTypeRule]
    default_suggestion: str
    version: str = "1.0"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "visa_type_selections"
        indexes = [
            [("country_code", pymongo.ASCENDING), ("version", pymongo.DESCENDING)],
            "default_suggestion"
        ]
