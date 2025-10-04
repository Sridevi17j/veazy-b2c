# models/visa_application.py
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    COLLECTING_BASIC_INFO = "collecting_basic_info"
    COLLECTING_DOCUMENTS = "collecting_documents"
    GENERATING_FORM = "generating_form"
    USER_REVIEWING_FORM = "user_reviewing_form"
    USER_APPROVED_FORM = "user_approved_form"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"
    USER_REVIEWED = "user_reviewed"

class BasicInfo(BaseModel):
    number_of_travellers: Optional[int] = None
    travel_purpose: Optional[str] = None
    approximate_travel_date: Optional[str] = None
    destination_country: Optional[str] = None

class SuggestedVisaType(BaseModel):
    visa_type: str
    confidence: float
    reasons: List[str]
    max_days: int
    visa_code: Optional[str] = None

class DocumentStatus(BaseModel):
    status: str  # "pending", "completed", "failed"
    document_id: Optional[str] = None
    extracted_info: Optional[Dict[str, Any]] = None

class CollectedData(BaseModel):
    passport: Optional[DocumentStatus] = None
    photo: Optional[DocumentStatus] = None
    travel_details: Optional[Dict[str, Any]] = None
    bank_statement: Optional[DocumentStatus] = None
    invitation_letter: Optional[DocumentStatus] = None

class WorkflowProgress(BaseModel):
    current_step: int = 0
    completed_steps: List[int] = []
    total_steps: int = 0
    progress_percentage: float = 0.0

class ValidationResult(BaseModel):
    status: ValidationStatus
    issues: List[str] = []

class ValidationResults(BaseModel):
    passport: Optional[ValidationResult] = None
    photo: Optional[ValidationResult] = None
    travel_details: Optional[ValidationResult] = None
    bank_statement: Optional[ValidationResult] = None
    overall_status: ValidationStatus = ValidationStatus.PENDING

class VisaApplication(Document):
    user_id: str = Field(index=True)
    status: ApplicationStatus = ApplicationStatus.COLLECTING_BASIC_INFO
    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    suggested_visa_types: List[SuggestedVisaType] = Field(default_factory=list)
    confirmed_visa_type: Optional[str] = None
    workflow_progress: WorkflowProgress = Field(default_factory=WorkflowProgress)
    collected_data: CollectedData = Field(default_factory=CollectedData)
    validation_results: ValidationResults = Field(default_factory=ValidationResults)
    generated_form: Optional[Dict[str, Any]] = None
    reference_number: Optional[str] = Field(default=None, index=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "visa_applications"
