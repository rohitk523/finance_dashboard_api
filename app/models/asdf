# app/models/transaction.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, condecimal

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_type: str  # income, expense, investment
    is_tax_deductible: bool = False
    tax_section: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    icon: Optional[str] = None
    
    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    amount: condecimal(max_digits=15, decimal_places=2)
    description: Optional[str] = None
    transaction_date: datetime
    category_id: Optional[int] = None
    transaction_type: str  # debit, credit
    payment_method: Optional[str] = None
    upi_id: Optional[str] = None
    bank_account_id: Optional[int] = None
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    is_tax_deductible: bool = False
    tax_section: Optional[str] = None
    gst_applicable: bool = False
    gst_amount: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    hsn_sac_code: Optional[str] = None
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    receipt_file: Optional[bytes] = None

class Transaction(TransactionBase):
    id: int
    user_id: int
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    
    class Config:
        orm_mode = True

class TransactionFilters(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    category_ids: Optional[List[int]] = None
    transaction_type: Optional[str] = None
    is_tax_deductible: Optional[bool] = None
    tax_section: Optional[str] = None
    payment_method: Optional[str] = None