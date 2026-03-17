from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: Optional[int] = Field(default=None, primary_key=True)
    account_number: str = Field(
        default_factory=lambda: str(uuid.uuid4()).replace("-", "")[:16].upper(),
        unique=True, index=True,
    )
    owner_id: int = Field(index=True)
    balance_cents: int = Field(default=0)
    currency: str = Field(default="INR", max_length=3)
    account_type: str = Field(default="savings")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
