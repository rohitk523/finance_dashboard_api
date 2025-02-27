# app/services/tax.py
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from fastapi import UploadFile, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import TaxReturn, TaxDeduction, Document, User, Transaction, Investment
from app.models.tax import TaxReturnCreate, TaxDeductionCreate, DocumentCreate, TaxCalculationInput, TaxCalculationResult
from app.utils.tax_calculator import IndianTaxCalculator
from app.services.storage import store_file

def create_tax_return(db: Session, tax_return_in: TaxReturnCreate, user_id: int) -> TaxReturn:
    """
    Create a new tax return.
    """
    db_tax_return = TaxReturn(
        user_id=user_id,
        fiscal_year=tax_return_in.fiscal_year,
        itr_form_type=tax_return_in.itr_form_type,
        filing_status=tax_return_in.filing_status,
        gross_total_income=tax_return_in.gross_total_income,
        total_deductions=tax_return_in.total_deductions,
        taxable_income=tax_return_in.taxable_income,
        tax_payable=tax_return_in.tax_payable,
        tds_amount=tax_return_in.tds_amount,
        tax_paid=tax_return_in.tax_paid,
        refund_amount=tax_return_in.refund_amount,
        refund_status=tax_return_in.refund_status,
        filing_date=tax_return_in.filing_date,
        acknowledgment_number=tax_return_in.acknowledgment_number,
        verification_method=tax_return_in.verification_method,
        verification_date=tax_return_in.verification_date
    )
    db.add(db_tax_return)
    db.commit()
    db.refresh(db_tax_return)
    return db_tax_return

def get_tax_return(db: Session, tax_return_id: int, user_id: int) -> Optional[TaxReturn]:
    """
    Get a tax return by ID, ensuring it belongs to the specified user.
    """
    return db.query(TaxReturn).filter(
        TaxReturn.id == tax_return_id,
        TaxReturn.user_id == user_id
    ).first()

def update_tax_return(db: Session, tax_return_id: int, tax_return_in: TaxReturnCreate) -> TaxReturn:
    """
    Update an existing tax return.
    """
    db_tax_return = db.query(TaxReturn).filter(TaxReturn.id == tax_return_id).first()
    
    if not db_tax_return:
        return None
    
    # Update fields
    for field, value in tax_return_in.dict().items():
        setattr(db_tax_return, field, value)
    
    db_tax_return.updated_at = datetime.now()
    db.commit()
    db.refresh(db_tax_return)
    return db_tax_return

def delete_tax_return(db: Session, tax_return_id: int) -> bool:
    """
    Delete a tax return.
    """
    db_tax_return = db.query(TaxReturn).filter(TaxReturn.id == tax_return_id).first()
    if not db_tax_return:
        return False
    
    db.delete(db_tax_return)
    db.commit()
    return True

def get_tax_returns(
    db: Session, 
    user_id: int,
    fiscal_year: Optional[str] = None,
    filing_status: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[TaxReturn]:
    """
    Get all tax returns for a user with optional filtering.
    """
    query = db.query(TaxReturn).filter(TaxReturn.user_id == user_id)
    
    if fiscal_year:
        query = query.filter(TaxReturn.fiscal_year == fiscal_year)
    
    if filing_status:
        query = query.filter(TaxReturn.filing_status == filing_status)
    
    return query.order_by(desc(TaxReturn.fiscal_year)).offset(skip).limit(limit).all()

def create_tax_deduction(db: Session, tax_return_id: int, deduction_in: TaxDeductionCreate) -> TaxDeduction:
    """
    Create a new tax deduction for a tax return.
    """
    db_deduction = TaxDeduction(
        tax_return_id=tax_return_id,
        section=deduction_in.section,
        description=deduction_in.description,
        amount=deduction_in.amount,
        proof_document_id=deduction_in.proof_document_id
    )
    db.add(db_deduction)
    db.commit()
    db.refresh(db_deduction)
    
    # Update total deductions in tax return
    update_tax_return_deductions(db, tax_return_id)
    
    return db_deduction

def get_tax_deductions(
    db: Session, 
    tax_return_id: int,
    section: Optional[str] = None
) -> List[TaxDeduction]:
    """
    Get all tax deductions for a tax return with optional filtering.
    """
    query = db.query(TaxDeduction).filter(TaxDeduction.tax_return_id == tax_return_id)
    
    if section:
        query = query.filter(TaxDeduction.section == section)
    
    return query.all()

def delete_tax_deduction(db: Session, deduction_id: int, user_id: int) -> bool:
    """
    Delete a tax deduction, ensuring it belongs to a tax return owned by the specified user.
    """
    # First, get the deduction and ensure it belongs to the user
    deduction = db.query(TaxDeduction).filter(TaxDeduction.id == deduction_id).first()
    if not deduction:
        return False
    
    # Get the associated tax return
    tax_return = db.query(TaxReturn).filter(
        TaxReturn.id == deduction.tax_return_id,
        TaxReturn.user_id == user_id
    ).first()
    
    if not tax_return:
        return False
    
    # Delete the deduction
    db.delete(deduction)
    db.commit()
    
    # Update total deductions in tax return
    update_tax_return_deductions(db, deduction.tax_return_id)
    
    return True

def update_tax_return_deductions(db: Session, tax_return_id: int) -> None:
    """
    Update the total deductions amount in a tax return based on its associated deductions.
    """
    deductions = db.query(TaxDeduction).filter(TaxDeduction.tax_return_id == tax_return_id).all()
    total_deductions = sum(float(deduction.amount) for deduction in deductions)
    
    tax_return = db.query(TaxReturn).filter(TaxReturn.id == tax_return_id).first()
    if tax_return:
        tax_return.total_deductions = total_deductions
        
        # Update taxable income and tax payable if gross income is set
        if tax_return.gross_total_income is not None:
            tax_return.taxable_income = max(0, float(tax_return.gross_total_income) - total_deductions)
            
            # Use tax calculator to determine tax payable
            calculator = IndianTaxCalculator(fiscal_year=tax_return.fiscal_year)
            user = db.query(User).filter(User.id == tax_return.user_id).first()
            age = 35  # Default value
            if user and user.date_of_birth:
                age = (datetime.now().date() - user.date_of_birth).days // 365
            
            # Get current deductions as dictionary
            deduction_dict = {}
            for deduction in deductions:
                deduction_dict[deduction.section] = float(deduction.amount)
            
            # Calculate tax
            tax_result = calculator.calculate_tax(
                income=float(tax_return.gross_total_income),
                age=age,
                is_new_regime=False,  # Assume old regime for now
                deductions=deduction_dict
            )
            
            tax_return.tax_payable = tax_result["total_tax_liability"]
        
        db.commit()

def upload_document(
    db: Session, 
    document_in: DocumentCreate, 
    user_id: int,
    file: UploadFile
) -> Document:
    """
    Upload a document and create document record.
    """
    # Store the file
    directory = f"documents/{user_id}"
    file_path = store_file(file, directory)
    
    # Create document record
    db_document = Document(
        user_id=user_id,
        document_type=document_in.document_type,
        document_name=document_in.document_name,
        file_path=file_path,
        file_size=os.path.getsize(os.path.join("uploads", file_path)) if file_path else 0,
        mime_type=file.content_type,
        fiscal_year=document_in.fiscal_year,
        related_entity_type=document_in.related_entity_type,
        related_entity_id=document_in.related_entity_id,
        notes=document_in.notes
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_documents(
    db: Session, 
    user_id: int,
    document_type: Optional[str] = None,
    fiscal_year: Optional[str] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Document]:
    """
    Get all documents for a user with optional filtering.
    """
    query = db.query(Document).filter(Document.user_id == user_id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if fiscal_year:
        query = query.filter(Document.fiscal_year == fiscal_year)
    
    if related_entity_type:
        query = query.filter(Document.related_entity_type == related_entity_type)
    
    if related_entity_id is not None:
        query = query.filter(Document.related_entity_id == related_entity_id)
    
    return query.order_by(desc(Document.upload_date)).offset(skip).limit(limit).all()

def get_document(db: Session, document_id: int, user_id: int) -> Optional[Document]:
    """
    Get a document by ID, ensuring it belongs to the specified user.
    """
    return db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id
    ).first()

def delete_document(db: Session, document_id: int) -> bool:
    """
    Delete a document.
    """
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if not db_document:
        return False
    
    # TODO: Delete the actual file from storage
    
    db.delete(db_document)
    db.commit()
    return True

def calculate_tax(db: Session, user_id: int, calculation_input: TaxCalculationInput) -> TaxCalculationResult:
    """
    Calculate tax liability based on input data.
    """
    # Get user details for age calculation
    user = db.query(User).filter(User.id == user_id).first()
    age = 35  # Default value
    if user and user.date_of_birth:
        age = (datetime.now().date() - user.date_of_birth).days // 365
    
    # Create tax calculator instance
    calculator = IndianTaxCalculator(fiscal_year=calculation_input.fiscal_year)
    
    # Prepare deductions dictionary
    deductions = calculation_input.deductions
    
    # Calculate tax for both regimes
    comparison = calculator.compare_tax_regimes(
        income=calculation_input.gross_salary + calculation_input.other_income + 
               calculation_input.house_property_income + calculation_input.capital_gains + 
               calculation_input.business_income,
        age=age,
        deductions=deductions
    )
    
    # Determine which ITR form is appropriate
    income_sources = []
    if calculation_input.gross_salary > 0:
        income_sources.append("salary")
    if calculation_input.house_property_income != 0:
        income_sources.append("house_property")
    if calculation_input.other_income > 0:
        income_sources.append("other_sources")
    if calculation_input.capital_gains != 0:
        income_sources.append("capital_gains")
    if calculation_input.business_income != 0:
        income_sources.append("business_income")
    
    has_capital_gains = calculation_input.capital_gains != 0
    has_business_income = calculation_input.business_income != 0
    
    itr_form = calculator.determine_itr_form(
        income_sources=income_sources,
        has_capital_gains=has_capital_gains,
        has_business_income=has_business_income
    )
    
    # Get tax saving suggestions
    saving_suggestions = calculator.get_tax_saving_suggestions(deductions)
    
    # Assume old regime for tax calculation result
    old_regime = comparison["old_regime"]
    
    # Prepare result
    result = TaxCalculationResult(
        fiscal_year=calculation_input.fiscal_year,
        gross_total_income=old_regime["gross_income"],
        total_deductions=old_regime["eligible_deductions"],
        taxable_income=old_regime["taxable_income"],
        tax_payable=old_regime["tax_liability"],
        education_cess=old_regime["education_cess"],
        total_tax_liability=old_regime["total_tax_liability"],
        recommended_itr_form=itr_form,
        monthly_tax_installment=old_regime["total_tax_liability"] / 12,
        tax_saving_potential=sum(suggestion["remaining_limit"] for suggestion in saving_suggestions 
                               if isinstance(suggestion["remaining_limit"], (int, float))),
        tax_saving_suggestions=[{
            "section": s["section"],
            "description": s["description"],
            "max_limit": s["max_limit"],
            "potential_saving": s["remaining_limit"] if isinstance(s["remaining_limit"], (int, float)) else 0,
            "recommendation": ", ".join([r["name"] for r in s["recommendations"]])
        } for s in saving_suggestions]
    )
    
    return result

def determine_itr_form(db: Session, user_id: int, fiscal_year: str) -> str:
    """
    Determine the appropriate ITR form based on user's financial data.
    """
    # Get user's income sources from transactions
    start_date, end_date = get_fiscal_year_dates(fiscal_year)
    
    # Check for various income sources
    has_salary = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "credit",
        Transaction.category_id.in_(db.query(Transaction).filter_by(name="Salary").with_entities(Transaction.id)),
        Transaction.transaction_date.between(start_date, end_date)
    ).count() > 0
    
    has_house_property = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "credit",
        Transaction.category_id.in_(db.query(Transaction).filter_by(name="Rent").with_entities(Transaction.id)),
        Transaction.transaction_date.between(start_date, end_date)
    ).count() > 0
    
    has_capital_gains = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "credit",
        Transaction.category_id.in_(db.query(Transaction).filter(Transaction.name.like("%Capital Gain%")).with_entities(Transaction.id)),
        Transaction.transaction_date.between(start_date, end_date)
    ).count() > 0
    
    has_business_income = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "credit",
        Transaction.category_id.in_(db.query(Transaction).filter(Transaction.name.like("%Business%")).with_entities(Transaction.id)),
        Transaction.transaction_date.between(start_date, end_date)
    ).count() > 0
    
    # Build list of income sources
    income_sources = []
    if has_salary:
        income_sources.append("salary")
    if has_house_property:
        income_sources.append("house_property")
    if has_capital_gains:
        income_sources.append("capital_gains")
    if has_business_income:
        income_sources.append("business_income")
    
    # Use tax calculator to determine ITR form
    calculator = IndianTaxCalculator(fiscal_year=fiscal_year)
    return calculator.determine_itr_form(
        income_sources=income_sources,
        has_capital_gains=has_capital_gains,
        has_foreign_income=False,  # We would need to check for foreign income separately
        has_business_income=has_business_income
    )

def get_fiscal_year_dates(fiscal_year: str) -> tuple:
    """
    Convert a fiscal year string (e.g., "2023-24") to start and end dates.
    """
    parts = fiscal_year.split("-")
    start_year = int(parts[0])
    end_year = start_year + 1
    
    start_date = datetime(start_year, 4, 1)
    end_date = datetime(end_year, 3, 31, 23, 59, 59)
    
    return start_date, end_date

def generate_itr_xml(db: Session, tax_return_id: int) -> str:
    """
    Generate ITR XML file for e-filing.
    """
    tax_return = db.query(TaxReturn).filter(TaxReturn.id == tax_return_id).first()
    if not tax_return:
        raise HTTPException(status_code=404, detail="Tax return not found")
    
    # Get user details
    user = db.query(User).filter(User.id == tax_return.user_id).first()
    
    # Get deductions
    deductions = db.query(TaxDeduction).filter(TaxDeduction.tax_return_id == tax_return_id).all()
    
    # Create XML root element
    root = ET.Element("ITR")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("form", tax_return.itr_form_type)
    root.set("assessment_year", tax_return.fiscal_year.replace("-", ""))
    
    # Add form data
    form_data = ET.SubElement(root, "FormData")
    
    # Add personal information
    personal_info = ET.SubElement(form_data, "PersonalInfo")
    ET.SubElement(personal_info, "Name").text = user.full_name
    ET.SubElement(personal_info, "PAN").text = user.pan_number or ""
    ET.SubElement(personal_info, "Address").text = user.address or ""
    ET.SubElement(personal_info, "Email").text = user.email
    ET.SubElement(personal_info, "MobileNo").text = user.phone or ""
    
    # Add income details
    income_details = ET.SubElement(form_data, "IncomeDetails")
    ET.SubElement(income_details, "GrossTotalIncome").text = str(tax_return.gross_total_income or 0)
    ET.SubElement(income_details, "TotalDeductions").text = str(tax_return.total_deductions or 0)
    ET.SubElement(income_details, "TaxableIncome").text = str(tax_return.taxable_income or 0)
    
    # Add deduction details
    deduction_details = ET.SubElement(form_data, "DeductionDetails")
    for deduction in deductions:
        deduction_item = ET.SubElement(deduction_details, "Deduction")
        ET.SubElement(deduction_item, "Section").text = deduction.section
        ET.SubElement(deduction_item, "Description").text = deduction.description
        ET.SubElement(deduction_item, "Amount").text = str(deduction.amount)
    
    # Add tax calculation
    tax_calculation = ET.SubElement(form_data, "TaxCalculation")
    ET.SubElement(tax_calculation, "TaxPayable").text = str(tax_return.tax_payable or 0)
    ET.SubElement(tax_calculation, "TDSAmount").text = str(tax_return.tds_amount or 0)
    ET.SubElement(tax_calculation, "TaxPaid").text = str(tax_return.tax_paid or 0)
    ET.SubElement(tax_calculation, "RefundAmount").text = str(tax_return.refund_amount or 0)
    
    # Convert to string
    xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    return xml_string

def get_tax_saving_suggestions(db: Session, user_id: int, fiscal_year: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get tax saving suggestions based on user's financial data.
    """
    # Use current fiscal year if not provided
    if not fiscal_year:
        calculator = IndianTaxCalculator()
        fiscal_year = calculator._get_current_fiscal_year()
    
    # Get start and end dates for the fiscal year
    start_date, end_date = get_fiscal_year_dates(fiscal_year)
    
    # Get user's tax deductions for the fiscal year
    deductions = {}
    
    # From tax returns
    tax_return = db.query(TaxReturn).filter(
        TaxReturn.user_id == user_id,
        TaxReturn.fiscal_year == fiscal_year
    ).first()
    
    if tax_return:
        tax_deductions = db.query(TaxDeduction).filter(
            TaxDeduction.tax_return_id == tax_return.id
        ).all()
        
        for deduction in tax_deductions:
            deductions[deduction.section] = float(deduction.amount)
    
    # From transactions marked as tax deductible
    tax_deductible_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_tax_deductible == True,
        Transaction.transaction_date.between(start_date, end_date)
    ).all()
    
    for transaction in tax_deductible_transactions:
        if transaction.tax_section:
            deductions[transaction.tax_section] = deductions.get(transaction.tax_section, 0) + float(transaction.amount)
    
    # From investments marked as tax saving
    tax_saving_investments = db.query(Investment).filter(
        Investment.user_id == user_id,
        Investment.is_tax_saving == True,
        Investment.investment_date.between(start_date, end_date)
    ).all()
    
    for investment in tax_saving_investments:
        if investment.tax_section:
            deductions[investment.tax_section] = deductions.get(investment.tax_section, 0) + float(investment.initial_amount)
    
    # Use tax calculator to get suggestions
    calculator = IndianTaxCalculator(fiscal_year=fiscal_year)
    suggestions = calculator.get_tax_saving_suggestions(deductions)
    
    # Convert to API response format
    result = []
    for suggestion in suggestions:
        result.append({
            "section": suggestion["section"],
            "description": suggestion["description"],
            "max_limit": suggestion["max_limit"],
            "current_amount": suggestion["current_amount"],
            "potential_saving": suggestion["remaining_limit"] if isinstance(suggestion["remaining_limit"], (int, float)) else 0,
            "recommendation": ", ".join([rec["name"] for rec in suggestion["recommendations"]])
        })
    
    return result

def get_tax_summary(db: Session, user_id: int, fiscal_year: Optional[str] = None) -> Dict[str, Any]:
    """
    Get tax summary for a user, optionally filtered by fiscal year.
    """
    # Use current fiscal year if not provided
    if not fiscal_year:
        calculator = IndianTaxCalculator()
        fiscal_year = calculator._get_current_fiscal_year()
    
    # Get start and end dates for the fiscal year
    start_date, end_date = get_fiscal_year_dates(fiscal_year)
    
    # Get income transactions for the period
    income_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "credit",
        Transaction.transaction_date.between(start_date, end_date)
    ).all()
    
    # Calculate total income
    total_income = sum(float(tx.amount) for tx in income_transactions)
    
    # Get tax deductible transactions
    tax_deductible_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_tax_deductible == True,
        Transaction.transaction_date.between(start_date, end_date)
    ).all()
    
    # Calculate total deductions from transactions
    total_deductions_from_transactions = sum(float(tx.amount) for tx in tax_deductible_transactions)
    
    # Get tax saving investments
    tax_saving_investments = db.query(Investment).filter(
        Investment.user_id == user_id,
        Investment.is_tax_saving == True,
        Investment.investment_date.between(start_date, end_date)
    ).all()
    
    # Calculate total deductions from investments
    total_deductions_from_investments = sum(float(inv.initial_amount) for inv in tax_saving_investments)
    
    # Get tax return for this fiscal year
    tax_return = db.query(TaxReturn).filter(
        TaxReturn.user_id == user_id,
        TaxReturn.fiscal_year == fiscal_year
    ).first()
    
    # Prepare result
    result = {
        "fiscal_year": fiscal_year,
        "total_income": total_income,
        "total_deductions": total_deductions_from_transactions + total_deductions_from_investments,
        "deductions_by_section": {},
        "tax_return_status": tax_return.filing_status if tax_return else "not_filed",
        "tax_return_id": tax_return.id if tax_return else None,
        "taxable_income": tax_return.taxable_income if tax_return else (total_income - total_deductions_from_transactions - total_deductions_from_investments),
        "tax_payable": tax_return.tax_payable if tax_return else 0,
        "tax_paid": tax_return.tax_paid if tax_return else 0,
        "tds_amount": tax_return.tds_amount if tax_return else 0,
        "refund_amount": tax_return.refund_amount if tax_return else 0,
        "refund_status": tax_return.refund_status if tax_return else None
    }
    
    # Calculate deductions by section
    deductions_by_section = {}
    
    # From transactions
    for tx in tax_deductible_transactions:
        if tx.tax_section:
            deductions_by_section[tx.tax_section] = deductions_by_section.get(tx.tax_section, 0) + float(tx.amount)
    
    # From investments
    for inv in tax_saving_investments:
        if inv.tax_section:
            deductions_by_section[inv.tax_section] = deductions_by_section.get(inv.tax_section, 0) + float(inv.initial_amount)
    
    result["deductions_by_section"] = deductions_by_section
    
    return result