from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class TransactionCreate(BaseModel):
    customer_name: str
    pages_bw: int = 0
    pages_color: int = 0
    photo_pages: int = 0


class TransactionUpdate(BaseModel):
    customer_name: Optional[str] = None
    pages_bw: Optional[int] = None
    pages_color: Optional[int] = None
    photo_pages: Optional[int] = None
    status: Optional[str] = None  # expected 'pending', 'completed', 'cancelled'


class TransactionRead(TransactionCreate):
    id: int
    total: float
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
