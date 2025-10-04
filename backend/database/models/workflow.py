# models/workflow.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ValidationRules(BaseModel):
    expiry_check: Optional[str] = None
    pages_required: Optional[str] = None
    quality: Optional[str] = None
    background: Optional[str] = None
    size: Optional[str] = None
    count: Optional[str] = None
    period: Optional[str] = None
    minimum_balance: Optional[str] = None
    format: Optional[str] = None

class FormField(BaseModel):
    name: str
    type: str  # "text", "date", "select", "number"
    required: bool = True
    label: Optional[str] = None
    options: Optional[List[str]] = None
    max: Optional[int] = None

class WorkflowStep(BaseModel):
    step_number: int
    step_type: str  # "document_collection", "information_collection"
    item_type: str
    title: str
    description: str
    required: bool = True
    validation_rules: Optional[ValidationRules] = None
    form_fields: Optional[List[FormField]] = None
    next_step: Optional[Any] = None  # Can be int or "complete"

class ProcessingInfo(BaseModel):
    processing_time: str
    visa_fee: float
    service_fee: Optional[float] = None
    total_fee: float
    currency: str = "USD"
    validity: Optional[str] = None
    entries: Optional[str] = None

class Workflow(BaseModel):
    country_code: str
    visa_type: str
    visa_code: str
    version: str = "1.0"
    workflow_steps: List[WorkflowStep]
    total_steps: int
    estimated_time: str
    processing_info: ProcessingInfo
    requirements_summary: Optional[List[str]] = None
