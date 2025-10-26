# Comprehensive Visa Application Model
# Purpose: Store complete visa application data following workflow JSON structure

from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    BASIC_INFO_COLLECTION = "basic_info_collection"
    VISA_RECOMMENDATION = "visa_recommendation"
    DOCUMENT_COLLECTION = "document_collection"
    PERSONAL_INFO = "personal_info"
    CONTACT_INFO = "contact_info"
    OCCUPATION_INFO = "occupation_info"
    TRAVEL_INFO = "travel_info"
    EMERGENCY_CONTACT = "emergency_contact"
    FINANCIAL_INFO = "financial_info"
    COMPLETE = "complete"
    SUBMITTED = "submitted"

class ExtractionMethod(str, Enum):
    USER_INPUT = "user_input"
    AI_DERIVE_FROM_NAME = "ai_derive_from_name"
    USER_ACCOUNT = "user_account"
    PASSPORT_BIO_PAGE = "passport_bio_page"
    VISA_TYPE_SELECTED = "visa_type_selected"
    FLIGHT_TICKETS_OR_USER_INPUT = "flight_tickets_or_user_input"
    HOTEL_RESERVATION_OR_USER_INPUT = "hotel_reservation_or_user_input"

# Document Storage Models
class DocumentInfo(BaseModel):
    file_path: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    extraction_status: str = "pending"  # pending, completed, failed
    extracted_data: Dict[str, Any] = Field(default_factory=dict)

class DocumentCollection(BaseModel):
    passport_bio_page: Optional[DocumentInfo] = None
    passport_photo: Optional[DocumentInfo] = None

# Workflow Stage Data Models
class PersonalInfo(BaseModel):
    # From passport bio page extraction
    surname: Optional[str] = None
    given_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    place_of_birth: Optional[str] = None
    passport_number: Optional[str] = None
    passport_type: Optional[str] = None
    passport_issuing_country: Optional[str] = None
    passport_issue_date: Optional[str] = None
    passport_expiry_date: Optional[str] = None
    
    # User input fields
    religion: Optional[str] = None
    marital_status: Optional[str] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

class Address(BaseModel):
    street_address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None

class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    permanent_address: Optional[Address] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

class OccupationInfo(BaseModel):
    occupation: Optional[str] = None
    employer_name: Optional[str] = None
    job_title: Optional[str] = None
    employer_address: Optional[Address] = None
    employer_phone_number: Optional[str] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

class TravelInfo(BaseModel):
    purpose_of_visit: Optional[str] = None
    intended_entry_date: Optional[str] = None
    intended_exit_date: Optional[str] = None
    expected_length_of_stay: Optional[int] = None
    residential_address_vietnam: Optional[str] = None
    province_city: Optional[str] = None
    ward_commune: Optional[str] = None
    entry_border_gate: Optional[str] = None
    exit_border_gate: Optional[str] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

class EmergencyContact(BaseModel):
    full_name: Optional[str] = None
    relationship: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[Address] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

class FinancialInfo(BaseModel):
    estimated_trip_expenses: Optional[float] = None
    have_health_insurance: Optional[bool] = None
    trip_expenses_covered_by: Optional[str] = None
    
    # Extraction metadata
    extraction_methods: Dict[str, str] = Field(default_factory=dict)

# Workflow Progress Tracking
class WorkflowProgress(BaseModel):
    current_stage: str = "documents"
    completed_stages: List[str] = Field(default_factory=list)
    stage_progress: Dict[str, Any] = Field(default_factory=dict)
    total_stages: int = 7

# Main Application Model
class ComprehensiveVisaApplication(Document):
    # Basic identification
    application_id: str = Field(index=True)
    thread_id: str = Field(index=True)  # Links to conversation
    user_id: Optional[str] = Field(default=None, index=True)
    
    # Application metadata
    visa_type: str = "Vietnam Tourism Single Entry"
    country_code: str = "VNM"
    status: ApplicationStatus = ApplicationStatus.BASIC_INFO_COLLECTION
    
    # Basic info (collected first)
    basic_info: Dict[str, Any] = Field(default_factory=dict)
    
    # Workflow progress
    workflow_progress: WorkflowProgress = Field(default_factory=WorkflowProgress)
    
    # Document collection
    documents: DocumentCollection = Field(default_factory=DocumentCollection)
    
    # Extracted and collected information by stage
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    occupation_info: OccupationInfo = Field(default_factory=OccupationInfo)
    travel_info: TravelInfo = Field(default_factory=TravelInfo)
    emergency_contact: EmergencyContact = Field(default_factory=EmergencyContact)
    financial_info: FinancialInfo = Field(default_factory=FinancialInfo)
    
    # Default values from workflow JSON
    default_values: Dict[str, Any] = Field(default_factory=lambda: {
        "previous_visits_to_vietnam": "No",
        "have_relatives_in_vietnam": "No",
        "criminal_record_status": "No",
        "deportation_history": "No",
        "multiple_nationalities": "No",
        "other_valid_passports": "No",
        "violation_vietnamese_laws": "No",
        "contact_agency_in_vietnam": "No",
        "visa_type": "Single Entry"
    })
    
    # Raw collected data (for flexibility)
    raw_collected_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "comprehensive_visa_applications"
        
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        
    def get_completion_percentage(self) -> float:
        """Calculate application completion percentage"""
        total_stages = self.workflow_progress.total_stages
        completed_stages = len(self.workflow_progress.completed_stages)
        return (completed_stages / total_stages) * 100 if total_stages > 0 else 0
        
    def is_stage_complete(self, stage: str) -> bool:
        """Check if a specific stage is complete"""
        return stage in self.workflow_progress.completed_stages