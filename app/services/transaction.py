# app/services/transaction.py
from datetime import datetime
from typing import List, Optional, Union

from fastapi import UploadFile
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.database.models import Transaction, TransactionCategory
from app.models.transaction import TransactionCreate, TransactionFilters, CategoryCreate
from app.services.storage import store_file

def create_transaction(
    db: Session, 
    transaction_in: TransactionCreate, 
    user_id: int,
    receipt_file: Optional[UploadFile] = None
) -> Transaction:
    """
    Create a new transaction.
    """
    receipt_url = None
    if receipt_file:
        receipt_url = store_file(receipt_file, f"receipts/{user_id}")
    
    db_transaction = Transaction(
        user_id=user_id,
        amount=transaction_in.amount,
        description=transaction_in.description,
        transaction_date=transaction_in.transaction_date,
        category_id=transaction_in.category_id,
        transaction_type=transaction_in.transaction_type,
        payment_method=transaction_in.payment_method,
        upi_id=transaction_in.upi_id,
        bank_account_id=transaction_in.bank_account_id,
        is_recurring=transaction_in.is_recurring,
        recurring_frequency=transaction_in.recurring_frequency,
        is_tax_deductible=transaction_in.is_tax_deductible,
        tax_section=transaction_in.tax_section,
        receipt_url=receipt_url,
        gst_applicable=transaction_in.gst_applicable,
        gst_amount=transaction_in.gst_amount,
        hsn_sac_code=transaction_in.hsn_sac_code,
        notes=transaction_in.notes
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transaction(db: Session, transaction_id: int, user_id: int) -> Optional[Transaction]:
    """
    Get a transaction by ID, ensuring it belongs to the specified user.
    """
    return db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    ).first()

def update_transaction(
    db: Session, 
    transaction_id: int, 
    transaction_in: TransactionCreate,
    receipt_file: Optional[UploadFile] = None
) -> Transaction:
    """
    Update an existing transaction.
    """
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    if not db_transaction:
        return None
    
    # Update receipt file if provided
    if receipt_file:
        receipt_url = store_file(receipt_file, f"receipts/{db_transaction.user_id}")
        db_transaction.receipt_url = receipt_url
    
    # Update other fields
    for field, value in transaction_in.dict(exclude={"receipt_file"}).items():
        setattr(db_transaction, field, value)
    
    db_transaction.updated_at = datetime.now()
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int) -> bool:
    """
    Delete a transaction.
    """
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True

def get_transactions(
    db: Session, 
    user_id: int, 
    filters: TransactionFilters,
    skip: int = 0, 
    limit: int = 100
) -> List[Transaction]:
    """
    Get all transactions for a user with optional filtering.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    # Apply filters
    if filters.start_date:
        query = query.filter(Transaction.transaction_date >= filters.start_date)
    if filters.end_date:
        query = query.filter(Transaction.transaction_date <= filters.end_date)
    if filters.min_amount is not None:
        query = query.filter(Transaction.amount >= filters.min_amount)
    if filters.max_amount is not None:
        query = query.filter(Transaction.amount <= filters.max_amount)
    if filters.category_ids:
        query = query.filter(Transaction.category_id.in_(filters.category_ids))
    if filters.transaction_type:
        query = query.filter(Transaction.transaction_type == filters.transaction_type)
    if filters.is_tax_deductible is not None:
        query = query.filter(Transaction.is_tax_deductible == filters.is_tax_deductible)
    if filters.tax_section:
        query = query.filter(Transaction.tax_section == filters.tax_section)
    if filters.payment_method:
        query = query.filter(Transaction.payment_method == filters.payment_method)
    
    return query.order_by(desc(Transaction.transaction_date)).offset(skip).limit(limit).all()

def get_recent_transactions(db: Session, user_id: int, limit: int = 5) -> List[Transaction]:
    """
    Get the most recent transactions for a user.
    """
    return db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.transaction_date)).limit(limit).all()

def create_category(db: Session, category_in: CategoryCreate) -> TransactionCategory:
    """
    Create a new transaction category.
    """
    db_category = TransactionCategory(
        name=category_in.name,
        description=category_in.description,
        category_type=category_in.category_type,
        is_tax_deductible=category_in.is_tax_deductible,
        tax_section=category_in.tax_section
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(
    db: Session, 
    category_type: Optional[str] = None,
    is_tax_deductible: Optional[bool] = None
) -> List[TransactionCategory]:
    """
    Get all transaction categories with optional filtering.
    """
    query = db.query(TransactionCategory)
    
    if category_type:
        query = query.filter(TransactionCategory.category_type == category_type)
    if is_tax_deductible is not None:
        query = query.filter(TransactionCategory.is_tax_deductible == is_tax_deductible)
    
    return query.all()

def get_category(db: Session, category_id: int) -> Optional[TransactionCategory]:
    """
    Get a category by ID.
    """
    return db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()

def update_category(db: Session, category_id: int, category_in: CategoryCreate) -> TransactionCategory:
    """
    Update an existing category.
    """
    db_category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    
    if not db_category:
        return None
    
    for field, value in category_in.dict().items():
        setattr(db_category, field, value)
    
    db_category.updated_at = datetime.now()
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> bool:
    """
    Delete a category.
    """
    db_category = db.query(TransactionCategory).filter(TransactionCategory.id == category_id).first()
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True