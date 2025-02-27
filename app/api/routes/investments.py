# app/api/routes/investments.py
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.database.db import get_db
from app.database.models import User
from app.models.investment import (
    Investment,
    InvestmentCreate,
    InvestmentType,
    InvestmentTypeCreate,
    InvestmentTransaction,
    InvestmentTransactionCreate,
    InvestmentInsights
)
from app.services.investment import (
    create_investment,
    get_investment,
    update_investment,
    delete_investment,
    get_investments,
    create_investment_type,
    get_investment_types,
    get_investment_type,
    update_investment_type,
    delete_investment_type,
    create_investment_transaction,
    get_investment_transactions,
    get_investment_transaction,
    update_investment_values,
    get_investment_insights
)

router = APIRouter()

# Investment endpoints
@router.post("", response_model=Investment)
def create_new_investment(
    investment_in: InvestmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new investment.
    """
    return create_investment(db=db, investment_in=investment_in, user_id=current_user.id)


@router.get("", response_model=List[Investment])
def read_investments(
    investment_type_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_tax_saving: Optional[bool] = None,
    tax_section: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all investments with optional filtering.
    """
    return get_investments(
        db=db, 
        user_id=current_user.id, 
        investment_type_id=investment_type_id,
        is_active=is_active,
        is_tax_saving=is_tax_saving,
        tax_section=tax_section,
        skip=skip, 
        limit=limit
    )


@router.get("/{investment_id}", response_model=Investment)
def read_investment(
    investment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific investment by ID.
    """
    investment = get_investment(db=db, investment_id=investment_id, user_id=current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return investment


@router.put("/{investment_id}", response_model=Investment)
def update_existing_investment(
    investment_id: int,
    investment_in: InvestmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update an investment.
    """
    investment = get_investment(db=db, investment_id=investment_id, user_id=current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return update_investment(db=db, investment_id=investment_id, investment_in=investment_in)


@router.delete("/{investment_id}")
def delete_existing_investment(
    investment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete an investment.
    """
    investment = get_investment(db=db, investment_id=investment_id, user_id=current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    delete_investment(db=db, investment_id=investment_id)
    return {"message": "Investment deleted successfully"}


# Investment Type endpoints
@router.post("/types", response_model=InvestmentType)
def create_new_investment_type(
    investment_type_in: InvestmentTypeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new investment type.
    """
    return create_investment_type(db=db, investment_type_in=investment_type_in)


@router.get("/types", response_model=List[InvestmentType])
def read_investment_types(
    risk_level: Optional[str] = None,
    is_tax_saving: Optional[bool] = None,
    tax_section: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all investment types with optional filtering.
    """
    return get_investment_types(
        db=db, 
        risk_level=risk_level,
        is_tax_saving=is_tax_saving,
        tax_section=tax_section
    )


@router.get("/types/{investment_type_id}", response_model=InvestmentType)
def read_investment_type(
    investment_type_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get a specific investment type by ID.
    """
    investment_type = get_investment_type(db=db, investment_type_id=investment_type_id)
    if not investment_type:
        raise HTTPException(status_code=404, detail="Investment type not found")
    return investment_type


@router.put("/types/{investment_type_id}", response_model=InvestmentType)
def update_existing_investment_type(
    investment_type_id: int,
    investment_type_in: InvestmentTypeCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update an investment type.
    """
    investment_type = get_investment_type(db=db, investment_type_id=investment_type_id)
    if not investment_type:
        raise HTTPException(status_code=404, detail="Investment type not found")
    return update_investment_type(db=db, investment_type_id=investment_type_id, investment_type_in=investment_type_in)


@router.delete("/types/{investment_type_id}")
def delete_existing_investment_type(
    investment_type_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Delete an investment type.
    """
    investment_type = get_investment_type(db=db, investment_type_id=investment_type_id)
    if not investment_type:
        raise HTTPException(status_code=404, detail="Investment type not found")
    delete_investment_type(db=db, investment_type_id=investment_type_id)
    return {"message": "Investment type deleted successfully"}


# Investment Transactions endpoints
@router.post("/{investment_id}/transactions", response_model=InvestmentTransaction)
def create_new_investment_transaction(
    investment_id: int,
    transaction_in: InvestmentTransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Create a new investment transaction.
    """
    investment = get_investment(db=db, investment_id=investment_id, user_id=current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return create_investment_transaction(db=db, investment_id=investment_id, transaction_in=transaction_in)


@router.get("/{investment_id}/transactions", response_model=List[InvestmentTransaction])
def read_investment_transactions(
    investment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get all transactions for a specific investment.
    """
    investment = get_investment(db=db, investment_id=investment_id, user_id=current_user.id)
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return get_investment_transactions(db=db, investment_id=investment_id)


@router.post("/update-values")
def update_investment_current_values(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Update current values of all investments.
    """
    updated = update_investment_values(db=db, user_id=current_user.id)
    return {"message": f"Updated {updated} investments"}


@router.get("/insights", response_model=InvestmentInsights)
def get_investment_portfolio_insights(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get insights and analytics on investment portfolio.
    """
    return get_investment_insights(db=db, user_id=current_user.id)