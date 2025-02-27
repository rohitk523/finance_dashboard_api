# app/api/routes/tax.py
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.db import get_db
from app.database.models import User
from app.models.tax import (
    TaxReturn,
    TaxReturnCreate,
    TaxDeduction,
    TaxDeductionCreate,
    Document,
    DocumentCreate,
    TaxCalculationInput,
    TaxCalculationResult,
    TaxSavingSuggestion,
    ITRFormType
)
from app.services.tax import (
    create_tax_return,
    get_tax_return,
    update_tax_return,
    delete_tax_return,
    get_tax_returns,
    create_tax_deduction,
    get_tax_deductions,
    delete_tax_deduction,
    upload_document,
    get_documents,
    get_document,
    delete_document,
    calculate_tax,
    determine_itr_form,
    generate_itr_xml,
    get_tax_saving_suggestions,
    get_tax_summary
)

router = APIRouter()

# Tax Return endpoints
@router.post("/returns", response_model=TaxReturn)
def create_new_tax_return(
    tax_return_in: TaxReturnCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new tax return.
    """
    return create_tax_return(db=db, tax_return_in=tax_return_in, user_id=current_user.id)


@router.get("/returns", response_model=List[TaxReturn])
def read_tax_returns(
    fiscal_year: Optional[str] = None,
    filing_status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all tax returns with optional filtering.
    """
    return get_tax_returns(
        db=db, 
        user_id=current_user.id, 
        fiscal_year=fiscal_year,
        filing_status=filing_status,
        skip=skip, 
        limit=limit
    )


@router.get("/returns/{tax_return_id}", response_model=TaxReturn)
def read_tax_return(
    tax_return_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific tax return by ID.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return tax_return


@router.put("/returns/{tax_return_id}", response_model=TaxReturn)
def update_existing_tax_return(
    tax_return_id: int,
    tax_return_in: TaxReturnCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a tax return.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return update_tax_return(db=db, tax_return_id=tax_return_id, tax_return_in=tax_return_in)


@router.delete("/returns/{tax_return_id}")
def delete_existing_tax_return(
    tax_return_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a tax return.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    delete_tax_return(db=db, tax_return_id=tax_return_id)
    return {"message": "Tax return deleted successfully"}


# Tax Deduction endpoints
@router.post("/returns/{tax_return_id}/deductions", response_model=TaxDeduction)
def create_new_tax_deduction(
    tax_return_id: int,
    deduction_in: TaxDeductionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new tax deduction for a tax return.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return create_tax_deduction(db=db, tax_return_id=tax_return_id, deduction_in=deduction_in)


@router.get("/returns/{tax_return_id}/deductions", response_model=List[TaxDeduction])
def read_tax_deductions(
    tax_return_id: int,
    section: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all tax deductions for a tax return with optional filtering.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    return get_tax_deductions(db=db, tax_return_id=tax_return_id, section=section)


@router.delete("/deductions/{deduction_id}")
def delete_existing_tax_deduction(
    deduction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a tax deduction.
    """
    # Ensure deduction belongs to the current user's tax return
    # This check would be handled in the service layer
    delete_tax_deduction(db=db, deduction_id=deduction_id, user_id=current_user.id)
    return {"message": "Tax deduction deleted successfully"}


# Document endpoints
@router.post("/documents/upload", response_model=Document)
def upload_tax_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    document_name: str = Form(...),
    fiscal_year: Optional[str] = Form(None),
    related_entity_type: Optional[str] = Form(None),
    related_entity_id: Optional[int] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Upload a tax document.
    """
    document_in = DocumentCreate(
        document_type=document_type,
        document_name=document_name,
        fiscal_year=fiscal_year,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        notes=notes,
        file_content=None  # Will be set from the file
    )
    return upload_document(db=db, document_in=document_in, user_id=current_user.id, file=file)


@router.get("/documents", response_model=List[Document])
def read_documents(
    document_type: Optional[str] = None,
    fiscal_year: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all documents with optional filtering.
    """
    return get_documents(
        db=db, 
        user_id=current_user.id,
        document_type=document_type,
        fiscal_year=fiscal_year,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        skip=skip,
        limit=limit
    )


@router.get("/documents/{document_id}", response_model=Document)
def read_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific document by ID.
    """
    document = get_document(db=db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.delete("/documents/{document_id}")
def delete_existing_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a document.
    """
    document = get_document(db=db, document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(db=db, document_id=document_id)
    return {"message": "Document deleted successfully"}


# Tax Calculation endpoints
@router.post("/calculate", response_model=TaxCalculationResult)
def calculate_tax_liability(
    calculation_input: TaxCalculationInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Calculate tax liability based on input data.
    """
    return calculate_tax(db=db, user_id=current_user.id, calculation_input=calculation_input)


@router.get("/itr-forms", response_model=List[str])
def get_itr_forms(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get list of ITR forms and their descriptions.
    """
    return [form.value for form in ITRFormType]


@router.post("/determine-itr-form")
def determine_appropriate_itr_form(
    fiscal_year: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Determine the appropriate ITR form based on user's financial data.
    """
    form_type = determine_itr_form(db=db, user_id=current_user.id, fiscal_year=fiscal_year)
    return {"itr_form_type": form_type}


@router.post("/generate-itr/{tax_return_id}")
def generate_itr_file(
    tax_return_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate ITR XML file for e-filing.
    """
    tax_return = get_tax_return(db=db, tax_return_id=tax_return_id, user_id=current_user.id)
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    
    xml_data = generate_itr_xml(db=db, tax_return_id=tax_return_id)
    return {"xml_data": xml_data}


@router.get("/saving-suggestions", response_model=List[TaxSavingSuggestion])
def get_tax_saving_options(
    fiscal_year: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get tax saving suggestions based on user's financial data.
    """
    return get_tax_saving_suggestions(db=db, user_id=current_user.id, fiscal_year=fiscal_year)


@router.get("/summary", response_model=dict)
def get_user_tax_summary(
    fiscal_year: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get tax summary for a user, optionally filtered by fiscal year.
    """
    return get_tax_summary(db=db, user_id=current_user.id, fiscal_year=fiscal_year)