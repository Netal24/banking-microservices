from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AccountCreate(BaseModel):
    owner_id: int
    currency: str = Field(default="INR", max_length=3)
    account_type: str = "savings"

class AccountRead(BaseModel):
    id: int
    account_number: str
    owner_id: int
    balance_cents: int
    currency: str
    account_type: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

class BalanceRead(BaseModel):
    account_id: int
    account_number: str
    balance: float
    currency: str
