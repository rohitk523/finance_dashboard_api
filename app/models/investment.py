# app/models/investment.py
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, condecimal

class InvestmentTypeBase(BaseModel):
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    min_investment: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    expected_returns: Optional[str] = None
    tax_implication: Optional[str] = None
    is_tax_saving: bool = False
    tax_section: Optional[str] = None
    lock_in_period: Optional[int] = None

class InvestmentTypeCreate(InvestmentTypeBase):
    pass

class InvestmentType(InvestmentTypeBase):
    id: int
    
    class Config:
        orm_mode = True

class InvestmentBase(BaseModel):
    investment_type_id: int
    name: str
    investment_date: date
    initial_amount: condecimal(max_digits=15, decimal_places=2)
    current_value: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    units: Optional[condecimal(max_digits=15, decimal_places=6)] = None
    maturity_date: Optional[date] = None
    interest_rate: Optional[condecimal(max_digits=5, decimal_places=2)] = None
    broker: Optional[str] = None
    folio_number: Optional[str] = None
    is_tax_saving: bool = False
    tax_section: Optional[str] = None
    is_active: bool = True
    notes: Optional[str] = None

class InvestmentCreate(InvestmentBase):
    pass

class Investment(InvestmentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    investment_type: InvestmentType
    
    class Config:
        orm_mode = True

class InvestmentTransactionBase(BaseModel):
    investment_id: int
    transaction_date: date
    transaction_type: str  # buy, sell, dividend, interest
    amount: condecimal(max_digits=15, decimal_places=2)
    units: Optional[condecimal(max_digits=15, decimal_places=6)] = None
    unit_price: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    notes: Optional[str] = None

class InvestmentTransactionCreate(InvestmentTransactionBase):
    pass

class InvestmentTransaction(InvestmentTransactionBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

class InvestmentInsights(BaseModel):
    total_invested: float
    current_value: float
    total_gain: float
    percentage_gain: float
    tax_saved: float
    best_performing: List[Investment]
    worst_performing: List[Investment]
    monthly_investment_trend: List[dict]