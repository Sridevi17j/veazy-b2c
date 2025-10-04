# models/payment.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(BaseModel):
    application_id: str
    amount: float
    currency: str = "USD"
    payment_type: str = "visa_fee"  # "visa_fee", "service_fee", "expedite_fee"
    provider: str  # "stripe", "paypal", etc.
    provider_payment_id: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
