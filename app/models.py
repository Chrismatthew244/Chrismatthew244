from datetime import date, datetime
from uuid import uuid4
from pydantic import BaseModel, Field


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    customer: str
    amount: float
    due_date: date
    status: str = "pending"


class Payment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    invoice_id: str
    transaction_reference: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InvoiceCreate(BaseModel):
    customer: str
    amount: float
    due_date: date


class PaymentCreate(BaseModel):
    invoice_id: str
    transaction_reference: str
