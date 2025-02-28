# scripts/seed_db.py
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database.db import SessionLocal, engine, Base
from app.database.models import (
    User, 
    UserPreference, 
    TransactionCategory, 
    Transaction,
    BankAccount,
    InvestmentType,
    Investment
)
from app.utils.security import get_password_hash

# Create sample data
def seed_database():
    db = SessionLocal()
    try:
        print("Creating sample data...")
        
        # Create user
        user = User(
            email="user@example.com",
            password_hash=get_password_hash("password@123"),
            full_name="Test User",
            phone="9876543210",
            pan_number="ABCDE1234F",
            aadhar_number="123456789012",
            date_of_birth=datetime(1990, 1, 1),
            address="123 Sample Street, Mumbai",
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user with ID: {user.id}")
        
        # Create user preferences
        preferences = UserPreference(
            user_id=user.id,
            notification_enabled=True,
            dashboard_customization='{"widgets": ["transactions", "investments", "tax_summary"]}',
            default_view="dashboard",
            preferred_language="en"
        )
        db.add(preferences)
        db.commit()
        
        # Create transaction categories
        categories = [
            {"name": "Salary", "description": "Income from employment", "category_type": "income", "icon": "wallet"},
            {"name": "Rent", "description": "Housing rent", "category_type": "expense", "icon": "home"},
            {"name": "Food", "description": "Groceries and dining", "category_type": "expense", "icon": "shopping-bag"},
            {"name": "Transportation", "description": "Public transport and fuel", "category_type": "expense", "icon": "truck"},
            {"name": "Entertainment", "description": "Movies, events, etc.", "category_type": "expense", "icon": "film"},
            {"name": "Medical", "description": "Healthcare expenses", "category_type": "expense", "icon": "activity", "is_tax_deductible": True, "tax_section": "80D"},
            {"name": "Education", "description": "Tuition and courses", "category_type": "expense", "icon": "book", "is_tax_deductible": True, "tax_section": "80E"},
            {"name": "Investment", "description": "Mutual funds, stocks, etc.", "category_type": "investment", "icon": "trending-up"},
            {"name": "Utility", "description": "Electricity, water, etc.", "category_type": "expense", "icon": "zap"},
            {"name": "Shopping", "description": "Clothes, electronics, etc.", "category_type": "expense", "icon": "shopping-cart"}
        ]
        
        for category_data in categories:
            category = TransactionCategory(**category_data)
            db.add(category)
        db.commit()
        print(f"Created {len(categories)} transaction categories")
        
        # Create bank accounts
        accounts_data = [
            {"user_id": user.id, "account_name": "Primary Savings", "bank_name": "HDFC Bank", "account_number": "1234567890", "ifsc_code": "HDFC0001234", "account_type": "savings", "balance": 50000},
            {"user_id": user.id, "account_name": "Salary Account", "bank_name": "ICICI Bank", "account_number": "9876543210", "ifsc_code": "ICIC0005678", "account_type": "savings", "balance": 75000}
        ]
        
        bank_accounts = []
        for account_data in accounts_data:
            account = BankAccount(**account_data)
            db.add(account)
            db.flush()  # Flush to get the ID without committing
            bank_accounts.append(account)
        db.commit()
        print(f"Created {len(accounts_data)} bank accounts")
        
        # Get all categories for reference
        all_categories = db.query(TransactionCategory).all()
        category_dict = {category.name: category for category in all_categories}
        
        # Create transactions
        today = datetime.now()
        transactions = []
        
        # Income transactions (salary)
        for month in range(6):
            salary_date = today.replace(day=1) - timedelta(days=month * 30)
            transactions.append({
                "user_id": user.id,
                "amount": 60000,
                "description": f"Salary for {salary_date.strftime('%B %Y')}",
                "transaction_date": salary_date,
                "category_id": category_dict["Salary"].id,
                "transaction_type": "credit",
                "payment_method": "bank_transfer",
                "bank_account_id": bank_accounts[1].id  # Use the actual ID, not account_number
            })
        
        # Expense transactions
        expense_categories = ["Rent", "Food", "Transportation", "Entertainment", "Utility", "Shopping"]
        for month in range(6):
            # Monthly rent
            rent_date = (today.replace(day=5) - timedelta(days=month * 30))
            transactions.append({
                "user_id": user.id,
                "amount": 15000,
                "description": f"Rent payment for {rent_date.strftime('%B %Y')}",
                "transaction_date": rent_date,
                "category_id": category_dict["Rent"].id,
                "transaction_type": "debit",
                "payment_method": "bank_transfer",
                "bank_account_id": bank_accounts[0].id  # Use the actual ID, not account_number
            })
            
            # Random daily expenses for this month
            for _ in range(20):
                expense_date = today - timedelta(days=random.randint(0, 180))
                category_name = random.choice(expense_categories)
                
                # Amount ranges by category
                amount_ranges = {
                    "Rent": (15000, 20000),
                    "Food": (200, 2000),
                    "Transportation": (100, 1500),
                    "Entertainment": (500, 3000),
                    "Utility": (1000, 5000),
                    "Shopping": (500, 10000),
                    "Medical": (500, 5000),
                    "Education": (1000, 20000)
                }
                
                amount_range = amount_ranges.get(category_name, (100, 1000))
                amount = round(random.uniform(*amount_range), 2)
                
                transactions.append({
                    "user_id": user.id,
                    "amount": amount,
                    "description": f"{category_name} expense",
                    "transaction_date": expense_date,
                    "category_id": category_dict[category_name].id,
                    "transaction_type": "debit",
                    "payment_method": random.choice(["upi", "card", "cash", "bank_transfer"]),
                    "bank_account_id": random.choice([acc.id for acc in bank_accounts])  # Use the actual IDs, not account_numbers
                })
        
        # Add tax-deductible medical expenses
        for _ in range(3):
            medical_date = today - timedelta(days=random.randint(0, 180))
            transactions.append({
                "user_id": user.id,
                "amount": random.uniform(5000, 15000),
                "description": "Health insurance premium",
                "transaction_date": medical_date,
                "category_id": category_dict["Medical"].id,
                "transaction_type": "debit",
                "payment_method": "card",
                "bank_account_id": bank_accounts[0].id,  # Use the actual ID, not account_number
                "is_tax_deductible": True,
                "tax_section": "80D"
            })
        
        # Create all transactions
        for transaction_data in transactions:
            transaction = Transaction(**transaction_data)
            db.add(transaction)
        
        db.commit()
        print(f"Created {len(transactions)} transactions")
        
        # Create investment types
        investment_types = [
            {"name": "Equity Mutual Fund", "description": "Diversified equity investments", "risk_level": "high", "min_investment": 500, "expected_returns": "12-15%", "tax_implication": "LTCG at 10% above ₹1 lakh, STCG at 15%"},
            {"name": "ELSS Mutual Fund", "description": "Tax-saving equity fund with 3-year lock-in", "risk_level": "high", "min_investment": 500, "expected_returns": "12-15%", "tax_implication": "LTCG at 10% above ₹1 lakh", "is_tax_saving": True, "tax_section": "80C", "lock_in_period": 36},
            {"name": "PPF", "description": "Public Provident Fund", "risk_level": "low", "min_investment": 500, "expected_returns": "7-8%", "tax_implication": "Tax-free returns", "is_tax_saving": True, "tax_section": "80C", "lock_in_period": 180},
            {"name": "Fixed Deposit", "description": "Bank fixed deposit", "risk_level": "low", "min_investment": 1000, "expected_returns": "5-7%", "tax_implication": "Interest taxable as per slab rate"},
            {"name": "NPS", "description": "National Pension System", "risk_level": "medium", "min_investment": 500, "expected_returns": "8-10%", "tax_implication": "40% of corpus tax-free on maturity", "is_tax_saving": True, "tax_section": "80CCD(1B)", "lock_in_period": 60}
        ]
        
        for type_data in investment_types:
            inv_type = InvestmentType(**type_data)
            db.add(inv_type)
        
        db.commit()
        print(f"Created {len(investment_types)} investment types")
        
        # Get investment types
        all_investment_types = db.query(InvestmentType).all()
        inv_type_dict = {inv_type.name: inv_type for inv_type in all_investment_types}
        
        # Create investments
        investments = [
            {
                "user_id": user.id,
                "investment_type_id": inv_type_dict["Equity Mutual Fund"].id,
                "name": "HDFC Index Fund",
                "investment_date": today - timedelta(days=180),
                "initial_amount": 50000,
                "current_value": 55000,
                "units": 1500.55,
                "broker": "Zerodha",
                "is_active": True
            },
            {
                "user_id": user.id,
                "investment_type_id": inv_type_dict["ELSS Mutual Fund"].id,
                "name": "Axis Long Term Equity Fund",
                "investment_date": today - timedelta(days=90),
                "initial_amount": 25000,
                "current_value": 26000,
                "units": 950.25,
                "broker": "Groww",
                "is_tax_saving": True,
                "tax_section": "80C",
                "is_active": True
            },
            {
                "user_id": user.id,
                "investment_type_id": inv_type_dict["PPF"].id,
                "name": "PPF Account",
                "investment_date": today - timedelta(days=365),
                "initial_amount": 150000,
                "current_value": 161250,
                "maturity_date": today + timedelta(days=365 * 15),
                "interest_rate": 7.5,
                "is_tax_saving": True,
                "tax_section": "80C",
                "is_active": True
            }
        ]
        
        for investment_data in investments:
            investment = Investment(**investment_data)
            db.add(investment)
        
        db.commit()
        print(f"Created {len(investments)} investments")
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed_database()