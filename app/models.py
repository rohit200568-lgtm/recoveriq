from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

PaymentStatus = Literal["failed", "pending", "captured", "halted", "manual_review"]

class PaymentEvent(BaseModel):
    payment_id: str
    customer_id: str
    amount: int = Field(gt=0, description="Amount in paise")
    currency: str = "INR"
    status: PaymentStatus = "failed"
    failure_reason: Optional[str] = None
    attempt_number: int = Field(default=1, ge=1)
    customer_language: str = "en"
    consent: bool = True
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

class RecoveryDecision(BaseModel):
    payment_id: str
    diagnosis: str
    action: Literal["retry", "reminder", "update_payment_method", "manual_review", "stop"]
    delay_hours: int = 0
    confidence: float
    reason: str
    policy_allowed: bool