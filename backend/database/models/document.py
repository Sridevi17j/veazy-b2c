# models/document.py
from beanie import Document
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class FileInfo(BaseModel):
    original_name: str
    s3_key: str
    file_size: int
    mime_type: str

class ExtractedData(BaseModel):
    full_name: Optional[str] = None
    passport_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    expiry_date: Optional[str] = None
    nationality: Optional[str] = None
    place_of_issue: Optional[str] = None
    gender: Optional[str] = None

class ConfidenceScores(BaseModel):
    overall: float
    fields: Dict[str, float] = {}

class DocumentModel(Document):
    user_id: str = Field(index=True)
    application_id: str = Field(index=True) 
    workflow_step: Optional[int] = None
    document_type: str = Field(index=True)  # "passport", "photo", "bank_statement", etc.
    file_info: FileInfo
    processing_status: str = Field(default="uploaded", index=True)  # "uploaded", "processing", "completed", "failed"
    extracted_data: ExtractedData = Field(default_factory=ExtractedData)
    confidence_scores: Optional[ConfidenceScores] = None
    validation_status: str = Field(default="pending", index=True)  # "pending", "approved", "rejected", "needs_review"
    validation_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection = "documents"
