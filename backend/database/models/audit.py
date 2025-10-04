# models/audit.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AuditEvent(BaseModel):
    application_id: Optional[str] = None
    user_id: Optional[str] = None
    event_type: str
    actor: str  # "user", "system", "admin"
    description: str
    metadata: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
