# app/api/routes/transactions.py
from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status, File, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.db import get_db
from app.database.models import User
from app.models.transaction import (
    Transaction,
    TransactionCreate,
    TransactionFilters,
    Category,
    CategoryCreate
)
from app.services.transaction import (
    create_transaction,
    get_transaction,
    update_transaction,
    delete_transaction,
    get_transactions,
    get_recent_transactions,
    create_category,
    get_categories,
    get_category,
    update_category,
    delete_category
)

router = APIRouter()

# Transaction endpoints
@router.post("", response_model=Transaction)
def create_new_transaction(
    transaction_in: TransactionCreate,
    receipt_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new transaction.
    """
    return create_transaction(db=db, transaction_in=transaction_in, user_id=current_user.id, receipt_file=receipt_file)


@router.get("", response_model=List[Transaction])
def read_transactions(
    filters: TransactionFilters = Depends(),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all transactions with optional filtering.
    """
    return get_transactions(db=db, user_id=current_user.id, filters=filters, skip=skip, limit=limit)


@router.get("/recent", response_model=List[Transaction])
def read_recent_transactions(
    limit: int = 5,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get recent transactions.
    """
    return get_recent_transactions(db=db, user_id=current_user.id, limit=limit)


@router.get("/{transaction_id}", response_model=Transaction)
def read_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific transaction by ID.
    """
    transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_existing_transaction(
    transaction_id: int,
    transaction_in: TransactionCreate,
    receipt_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a transaction.
    """
    transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return update_transaction(
        db=db, 
        transaction_id=transaction_id, 
        transaction_in=transaction_in,
        receipt_file=receipt_file
    )


@router.delete("/{transaction_id}")
def delete_existing_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a transaction.
    """
    transaction = get_transaction(db=db, transaction_id=transaction_id, user_id=current_user.id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    delete_transaction(db=db, transaction_id=transaction_id)
    return {"message": "Transaction deleted successfully"}


# Category endpoints
@router.post("/categories", response_model=Category)
def create_new_category(
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new transaction category.
    """
    return create_category(db=db, category_in=category_in)


@router.get("/categories", response_model=List[Category])
def read_categories(
    category_type: Optional[str] = None,
    is_tax_deductible: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all transaction categories with optional filtering.
    """
    return get_categories(
        db=db, 
        category_type=category_type, 
        is_tax_deductible=is_tax_deductible
    )


@router.get("/categories/{category_id}", response_model=Category)
def read_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific transaction category by ID.
    """
    category = get_category(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/categories/{category_id}", response_model=Category)
def update_existing_category(
    category_id: int,
    category_in: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update a transaction category.
    """
    category = get_category(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return update_category(db=db, category_id=category_id, category_in=category_in)


@router.delete("/categories/{category_id}")
def delete_existing_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete a transaction category.
    """
    category = get_category(db=db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(db=db, category_id=category_id)
    return {"message": "Category deleted successfully"}