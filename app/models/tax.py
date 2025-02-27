# app/models/tax.py
from datetime import date, datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, condecimal

class ITRFormType(str, Enum):
    ITR_1 = "ITR-1"
    ITR_2 = "ITR-2"
    ITR_3 = "ITR-3"
    ITR_4 = "ITR-4"

class FilingStatus(str, Enum):
    DRAFT = "draft"
    FILED = "filed"
    VERIFIED = "verified"

class TaxSectionEnum(str, Enum):
    SEC_80C = "80C"
    SEC_80D = "80D"
    SEC_80E = "80E"
    SEC_80G = "80G"
    SEC_80TTA = "80TTA"
    SEC_80TTB = "80TTB"
    SEC_HRA = "HRA"
    SEC_LTA = "LTA"
    OTHER = "other"

class DocumentType(str, Enum):
    INCOME_PROOF = "income_proof"
    TAX_FORM = "tax_form"
    INVESTMENT_PROOF = "investment_proof"
    RECEIPT = "receipt"
    OTHER = "other"

class TaxDeductionBase(BaseModel):
    section: str
    description: str
    amount: condecimal(max_digits=15, decimal_places=2)
    proof_document_id: Optional[int] = None

class TaxDeductionCreate(TaxDeductionBase):
    pass

class TaxDeduction(TaxDeductionBase):
    id: int
    tax_return_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TaxReturnBase(BaseModel):
    fiscal_year: str  # 2023-24
    itr_form_type: ITRFormType
    filing_status: FilingStatus = FilingStatus.DRAFT
    gross_total_income: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    total_deductions: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    taxable_income: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    tax_payable: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    tds_amount: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    tax_paid: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    refund_amount: Optional[condecimal(max_digits=15, decimal_places=2)] = None
    refund_status: Optional[str] = None
    filing_date: Optional[date] = None
    acknowledgment_number: Optional[str] = None
    verification_method: Optional[str] = None
    verification_date: Optional[date] = None

class TaxReturnCreate(TaxReturnBase):
    pass

class TaxReturn(TaxReturnBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    deductions: List[TaxDeduction] = []
    
    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    document_type: DocumentType
    document_name: str
    fiscal_year: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    notes: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_content: bytes

class Document(DocumentBase):
    id: int
    user_id: int
    file_path: str
    file_size: int
    mime_type: str
    upload_date: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class TaxCalculationInput(BaseModel):
    fiscal_year: str
    gross_salary: float
    other_income: Optional[float] = 0
    house_property_income: Optional[float] = 0
    capital_gains: Optional[float] = 0
    business_income: Optional[float] = 0
    deductions: dict  # A dictionary with section as key and amount as value

class TaxCalculationResult(BaseModel):
    fiscal_year: str
    gross_total_income: float
    total_deductions: float
    taxable_income: float
    tax_payable: float
    education_cess: float
    surcharge: Optional[float] = 0
    total_tax_liability: float
    recommended_itr_form: ITRFormType
    monthly_tax_installment: float
    tax_saving_potential: Optional[float] = None
    tax_saving_suggestions: List[dict] = []

class TaxSavingSuggestion(BaseModel):
    section: str
    description: str
    max_limit: float
    potential_saving: float
    recommendation: str