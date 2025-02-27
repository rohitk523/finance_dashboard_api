# app/services/investment.py
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from dateutil.relativedelta import relativedelta

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.models import Investment, InvestmentType, InvestmentTransaction
from app.models.investment import InvestmentCreate, InvestmentTypeCreate, InvestmentTransactionCreate, InvestmentInsights

def create_investment(db: Session, investment_in: InvestmentCreate, user_id: int) -> Investment:
    """
    Create a new investment.
    """
    # Check if investment type exists
    db_investment_type = db.query(InvestmentType).filter(InvestmentType.id == investment_in.investment_type_id).first()
    if not db_investment_type:
        raise ValueError("Investment type not found")
    
    # Create investment
    db_investment = Investment(
        user_id=user_id,
        investment_type_id=investment_in.investment_type_id,
        name=investment_in.name,
        investment_date=investment_in.investment_date,
        initial_amount=investment_in.initial_amount,
        current_value=investment_in.current_value or investment_in.initial_amount,  # Default to initial amount
        units=investment_in.units,
        maturity_date=investment_in.maturity_date,
        interest_rate=investment_in.interest_rate,
        broker=investment_in.broker,
        folio_number=investment_in.folio_number,
        is_tax_saving=investment_in.is_tax_saving,
        tax_section=investment_in.tax_section,
        is_active=investment_in.is_active,
        notes=investment_in.notes
    )
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    
    # Create initial investment transaction
    create_investment_transaction(
        db=db,
        investment_id=db_investment.id,
        transaction_in=InvestmentTransactionCreate(
            investment_id=db_investment.id,
            transaction_date=investment_in.investment_date,
            transaction_type="buy",
            amount=investment_in.initial_amount,
            units=investment_in.units,
            unit_price=None if not investment_in.units else investment_in.initial_amount / investment_in.units,
            notes="Initial investment"
        )
    )
    
    return db_investment

def get_investment(db: Session, investment_id: int, user_id: int) -> Optional[Investment]:
    """
    Get an investment by ID, ensuring it belongs to the specified user.
    """
    return db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == user_id
    ).first()

def update_investment(db: Session, investment_id: int, investment_in: InvestmentCreate) -> Investment:
    """
    Update an existing investment.
    """
    db_investment = db.query(Investment).filter(Investment.id == investment_id).first()
    
    if not db_investment:
        return None
    
    # Check if investment type exists if it's being changed
    if investment_in.investment_type_id != db_investment.investment_type_id:
        db_investment_type = db.query(InvestmentType).filter(InvestmentType.id == investment_in.investment_type_id).first()
        if not db_investment_type:
            raise ValueError("Investment type not found")
    
    # Update fields
    for field, value in investment_in.dict().items():
        setattr(db_investment, field, value)
    
    db_investment.updated_at = datetime.now()
    db.commit()
    db.refresh(db_investment)
    return db_investment

def delete_investment(db: Session, investment_id: int) -> bool:
    """
    Delete an investment.
    """
    db_investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not db_investment:
        return False
    
    # The associated investment transactions will be deleted automatically due to cascade
    db.delete(db_investment)
    db.commit()
    return True

def get_investments(
    db: Session, 
    user_id: int,
    investment_type_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_tax_saving: Optional[bool] = None,
    tax_section: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[Investment]:
    """
    Get all investments for a user with optional filtering.
    """
    query = db.query(Investment).filter(Investment.user_id == user_id)
    
    if investment_type_id:
        query = query.filter(Investment.investment_type_id == investment_type_id)
    
    if is_active is not None:
        query = query.filter(Investment.is_active == is_active)
    
    if is_tax_saving is not None:
        query = query.filter(Investment.is_tax_saving == is_tax_saving)
    
    if tax_section:
        query = query.filter(Investment.tax_section == tax_section)
    
    return query.order_by(desc(Investment.investment_date)).offset(skip).limit(limit).all()

def create_investment_type(db: Session, investment_type_in: InvestmentTypeCreate) -> InvestmentType:
    """
    Create a new investment type.
    """
    db_investment_type = InvestmentType(
        name=investment_type_in.name,
        description=investment_type_in.description,
        risk_level=investment_type_in.risk_level,
        min_investment=investment_type_in.min_investment,
        expected_returns=investment_type_in.expected_returns,
        tax_implication=investment_type_in.tax_implication,
        is_tax_saving=investment_type_in.is_tax_saving,
        tax_section=investment_type_in.tax_section,
        lock_in_period=investment_type_in.lock_in_period
    )
    db.add(db_investment_type)
    db.commit()
    db.refresh(db_investment_type)
    return db_investment_type

def get_investment_types(
    db: Session,
    risk_level: Optional[str] = None,
    is_tax_saving: Optional[bool] = None,
    tax_section: Optional[str] = None
) -> List[InvestmentType]:
    """
    Get all investment types with optional filtering.
    """
    query = db.query(InvestmentType)
    
    if risk_level:
        query = query.filter(InvestmentType.risk_level == risk_level)
    
    if is_tax_saving is not None:
        query = query.filter(InvestmentType.is_tax_saving == is_tax_saving)
    
    if tax_section:
        query = query.filter(InvestmentType.tax_section == tax_section)
    
    return query.all()

def get_investment_type(db: Session, investment_type_id: int) -> Optional[InvestmentType]:
    """
    Get an investment type by ID.
    """
    return db.query(InvestmentType).filter(InvestmentType.id == investment_type_id).first()

def update_investment_type(db: Session, investment_type_id: int, investment_type_in: InvestmentTypeCreate) -> InvestmentType:
    """
    Update an existing investment type.
    """
    db_investment_type = db.query(InvestmentType).filter(InvestmentType.id == investment_type_id).first()
    
    if not db_investment_type:
        return None
    
    for field, value in investment_type_in.dict().items():
        setattr(db_investment_type, field, value)
    
    db_investment_type.updated_at = datetime.now()
    db.commit()
    db.refresh(db_investment_type)
    return db_investment_type

def delete_investment_type(db: Session, investment_type_id: int) -> bool:
    """
    Delete an investment type.
    """
    # Check if there are investments using this type
    has_investments = db.query(Investment).filter(Investment.investment_type_id == investment_type_id).first() is not None
    if has_investments:
        raise ValueError("Cannot delete investment type that is being used by investments")
    
    db_investment_type = db.query(InvestmentType).filter(InvestmentType.id == investment_type_id).first()
    if not db_investment_type:
        return False
    
    db.delete(db_investment_type)
    db.commit()
    return True

def create_investment_transaction(
    db: Session, 
    investment_id: int,
    transaction_in: InvestmentTransactionCreate
) -> InvestmentTransaction:
    """
    Create a new investment transaction.
    """
    # Check if investment exists
    db_investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not db_investment:
        raise ValueError("Investment not found")
    
    # Create transaction
    db_transaction = InvestmentTransaction(
        investment_id=investment_id,
        transaction_date=transaction_in.transaction_date,
        transaction_type=transaction_in.transaction_type,
        amount=transaction_in.amount,
        units=transaction_in.units,
        unit_price=transaction_in.unit_price,
        notes=transaction_in.notes
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Update investment based on transaction
    update_investment_after_transaction(db, db_investment, db_transaction)
    
    return db_transaction

def update_investment_after_transaction(db: Session, investment: Investment, transaction: InvestmentTransaction) -> None:
    """
    Update investment details after a transaction.
    """
    if transaction.transaction_type == "buy":
        # Add units and value for buy transaction
        if transaction.units is not None:
            investment.units = (investment.units or 0) + transaction.units
        investment.current_value = float(investment.current_value or 0) + float(transaction.amount)
    
    elif transaction.transaction_type == "sell":
        # Subtract units and value for sell transaction
        if transaction.units is not None:
            investment.units = max(0, (investment.units or 0) - transaction.units)
        investment.current_value = max(0, float(investment.current_value or 0) - float(transaction.amount))
        
        # If all units sold, mark as inactive
        if investment.units == 0 or investment.current_value == 0:
            investment.is_active = False
    
    elif transaction.transaction_type == "dividend" or transaction.transaction_type == "interest":
        # For dividends and interest, just record the transaction, don't change units
        pass
    
    db.commit()

def get_investment_transactions(db: Session, investment_id: int) -> List[InvestmentTransaction]:
    """
    Get all transactions for a specific investment.
    """
    return db.query(InvestmentTransaction).filter(
        InvestmentTransaction.investment_id == investment_id
    ).order_by(desc(InvestmentTransaction.transaction_date)).all()

def get_investment_transaction(db: Session, transaction_id: int) -> Optional[InvestmentTransaction]:
    """
    Get an investment transaction by ID.
    """
    return db.query(InvestmentTransaction).filter(InvestmentTransaction.id == transaction_id).first()

def update_investment_values(db: Session, user_id: int) -> int:
    """
    Update current values of all investments.
    This is a placeholder for what would typically be integration with a market data API.
    """
    # Get active investments
    investments = db.query(Investment).filter(
        Investment.user_id == user_id,
        Investment.is_active == True
    ).all()
    
    updated_count = 0
    
    for investment in investments:
        # This is where you'd typically fetch current market value from an API
        # For now, we'll use a simple calculation for demonstration
        
        # Example: For fixed income, calculate accrued interest
        if investment.interest_rate is not None:
            days_invested = (datetime.now().date() - investment.investment_date).days
            years = days_invested / 365.0
            new_value = float(investment.initial_amount) * (1 + float(investment.interest_rate) / 100) ** years
            investment.current_value = new_value
            updated_count += 1
        
        # Example: For mutual funds, stock, etc. we'd fetch NAV/price from API
        # This is just a placeholder logic
        elif investment.units is not None:
            # Simulate random market fluctuation (in reality would fetch from API)
            # This is dummy logic for demonstration only
            import random
            # Simulate +/- 1% random fluctuation
            fluctuation = 1 + (random.random() * 0.02 - 0.01)
            unit_price = float(investment.current_value) / float(investment.units) * fluctuation
            investment.current_value = float(investment.units) * unit_price
            updated_count += 1
    
    db.commit()
    return updated_count

def get_investment_insights(db: Session, user_id: int) -> InvestmentInsights:
    """
    Get insights and analytics on investment portfolio.
    """
    # Get all investments
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    
    # Calculate totals
    total_invested = sum(float(inv.initial_amount) for inv in investments)
    current_value = sum(float(inv.current_value or inv.initial_amount) for inv in investments)
    total_gain = current_value - total_invested
    percentage_gain = (total_gain / total_invested * 100) if total_invested > 0 else 0
    
    # Calculate tax saved
    tax_saved = 0
    tax_saving_investments = [inv for inv in investments if inv.is_tax_saving]
    for inv in tax_saving_investments:
        # Simple assumption: 30% tax bracket
        tax_saved += float(inv.initial_amount) * 0.3
    
    # Find best and worst performers
    for inv in investments:
        # Calculate returns
        inv_gain = float(inv.current_value or inv.initial_amount) - float(inv.initial_amount)
        inv_percentage = (inv_gain / float(inv.initial_amount) * 100) if float(inv.initial_amount) > 0 else 0
        # Store in a temporary attribute
        inv.return_percentage = inv_percentage
    
    # Sort by return percentage
    sorted_investments = sorted(investments, key=lambda x: x.return_percentage, reverse=True)
    best_performing = sorted_investments[:3] if len(sorted_investments) >= 3 else sorted_investments
    worst_performing = sorted_investments[-3:] if len(sorted_investments) >= 3 else sorted_investments
    worst_performing.reverse()  # Show worst first
    
    # Get investment trend over the last 12 months
    today = datetime.now().date()
    monthly_investment_trend = []
    
    for i in range(11, -1, -1):
        month_start = today.replace(day=1) - relativedelta(months=i)
        month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
        
        # Get investments made in this month
        month_investments = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.investment_date.between(month_start, month_end)
        ).all()
        
        month_total = sum(float(inv.initial_amount) for inv in month_investments)
        
        monthly_investment_trend.append({
            "month": month_start.strftime("%b %Y"),
            "amount": month_total
        })
    
    return InvestmentInsights(
        total_invested=total_invested,
        current_value=current_value,
        total_gain=total_gain,
        percentage_gain=percentage_gain,
        tax_saved=tax_saved,
        best_performing=best_performing,
        worst_performing=worst_performing,
        monthly_investment_trend=monthly_investment_trend
    )