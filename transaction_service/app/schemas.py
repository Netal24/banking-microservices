from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime

class TransferRequest(BaseModel):
    source_account_id: int = Field(gt=0)
    destination_account_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", max_length=3)
    reference: Optional[str] = None
    user_id: int = Field(gt=0)

class DepositRequest(BaseModel):
    account_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", max_length=3)
    reference: Optional[str] = None

class WithdrawRequest(BaseModel):
    account_id: int = Field(gt=0)
    amount: float = Field(gt=0)
    currency: str = Field(default="INR", max_length=3)
    user_id: int = Field(gt=0)
    reference: Optional[str] = None

class TransactionRead(BaseModel):
    id: int
    source_account_id: int
    destination_account_id: int
    amount_cents: int
    currency: str
    transaction_type: str
    status: str
    reference: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

class TransactionResponse(BaseModel):
    transaction_id: int
    status: Literal["completed", "failed", "flagged"]
    message: str
