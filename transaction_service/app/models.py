from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    account_number: str = Field(unique=True, index=True)
    owner_id: int = Field(index=True)
    balance_cents: int = Field(default=0)
    currency: str = Field(default="INR")
    account_type: str = Field(default="savings")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"
    id: Optional[int] = Field(default=None, primary_key=True)
    source_account_id: int = Field(index=True)
    destination_account_id: int = Field(index=True)
    amount_cents: int = Field(gt=0)
    currency: str = Field(max_length=3)
    transaction_type: str = Field(default="transfer")
    status: str = Field(default="completed")
    reference: Optional[str] = Field(default=None, max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)
