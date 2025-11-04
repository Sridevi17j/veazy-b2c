# models/visa_application.py
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"

class BasicInfo(BaseModel):
    country: Optional[str] = None
    country_code: Optional[str] = None
    visa_type: Optional[str] = None
    purpose: Optional[str] = None
    number_of_travelers: Optional[int] = None
    travel_dates: Optional[Dict[str, Any]] = Field(default_factory=dict)  # {"entry_date": "", "exit_date": ""}

class WorkflowInfo(BaseModel):
    workflow_file: Optional[str] = None  # e.g., "VNM_tourism_single_entry_workflow.json"
    current_stage: Optional[str] = None  # e.g., "stage_1_documents"
    completed_stages: List[str] = Field(default_factory=list)
    stage_progress: Dict[str, Any] = Field(default_factory=dict)

class DocumentInfo(BaseModel):
    file_path: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    file_type: Optional[str] = None
    extraction_status: str = "pending"  # pending, completed, failed
    extracted_data: Dict[str, Any] = Field(default_factory=dict)

class TravelerData(BaseModel):
    traveler_id: int
    is_primary_applicant: bool = False
    documents: Dict[str, DocumentInfo] = Field(default_factory=dict)  # Dynamic: {"passport_bio_page": DocumentInfo, ...}
    collected_data: Dict[str, Any] = Field(default_factory=dict)  # Dynamic: {"personal_info": {...}, "contact_info": {...}}

class VisaApplication(Document):
    # Unique identifiers
    visa_application_id: Optional[str] = Field(default=None, index=True)  # Custom format: VA_{user_id}_{date}_{counter}
    user_id: str = Field(index=True)

    # Status tracking
    status: ApplicationStatus = ApplicationStatus.IN_PROGRESS

    # Basic information (from Phase 1 collection)
    basic_info: BasicInfo = Field(default_factory=BasicInfo)

    # Workflow tracking
    workflow_info: WorkflowInfo = Field(default_factory=WorkflowInfo)

    # Multi-traveler support with dynamic data structure
    travelers: List[TravelerData] = Field(default_factory=list)

    # Additional metadata
    completion_percentage: float = 0.0
    automation_js_file: Optional[Dict[str, Any]] = None  # {"file_path": "", "generated_at": ""}
    submission_timestamp: Optional[datetime] = None
    decision_date: Optional[datetime] = None
    processed_by: Optional[str] = None

    # Status history for audit trail
    status_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection = "visa_applications"

    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()

    async def update_status(self, new_status: ApplicationStatus, metadata: Dict[str, Any] = None):
        """Update application status with timestamp and audit trail"""
        self.status = new_status
        self.update_timestamp()

        # Add to status history
        self.status_history.append({
            "status": new_status,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        })

        await self.save()

    def get_primary_traveler(self) -> Optional[TravelerData]:
        """Get the primary applicant traveler"""
        for traveler in self.travelers:
            if traveler.is_primary_applicant:
                return traveler
        return self.travelers[0] if self.travelers else None
