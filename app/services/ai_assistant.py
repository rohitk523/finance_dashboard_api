# app/services/ai_assistant.py
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json
import re

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.database.models import (
    AIAssistantConversation, 
    User, 
    Transaction, 
    Investment, 
    TransactionCategory,
    InvestmentType,
    TaxReturn
)
from app.models.ai_assistant import (
    AIAssistantQuery,
    AIAssistantResponse,
    ExpenseAnalysisRequest,
    ExpenseAnalysisResponse,
    TaxAdviceRequest,
    TaxAdviceResponse,
    InvestmentRecommendationRequest,
    InvestmentRecommendationResponse
)
from app.config import settings
from app.utils.tax_calculator import IndianTaxCalculator

def process_assistant_query(db: Session, query: AIAssistantQuery) -> AIAssistantResponse:
    """
    Process a general query to the AI assistant.
    """
    # In a real application, this would call an AI service API
    # For demonstration, we'll use rule-based responses

    # Extract keywords from query
    keywords = extract_keywords(query.query_text)
    
    # Generate response based on query type and keywords
    response_text = ""
    data = {}
    suggestions = []
    
    if query.query_type == "expense_analysis":
        if "budget" in keywords:
            response_text = "Based on your spending patterns, I recommend a monthly budget of ₹30,000 for essentials and ₹15,000 for discretionary spending."
            suggestions = [
                {"type": "action", "text": "Create a detailed budget", "action": "create_budget"},
                {"type": "action", "text": "Analyze your expenses", "action": "analyze_expenses"}
            ]
        elif "reduce" in keywords or "save" in keywords:
            response_text = "I notice you spent ₹4,500 on dining out last month. Reducing this by half could save you ₹27,000 annually."
            suggestions = [
                {"type": "action", "text": "See top spending categories", "action": "show_top_expenses"},
                {"type": "action", "text": "Get saving tips", "action": "get_saving_tips"}
            ]
        else:
            response_text = "I can help you analyze your expenses. Would you like to see your spending breakdown, budget recommendations, or saving opportunities?"
            suggestions = [
                {"type": "action", "text": "Spending breakdown", "action": "show_spending_breakdown"},
                {"type": "action", "text": "Budget recommendations", "action": "show_budget_recommendations"},
                {"type": "action", "text": "Saving opportunities", "action": "show_saving_opportunities"}
            ]
    
    elif query.query_type == "tax_advice":
        if "deduction" in keywords or "section" in keywords:
            response_text = "You can claim deductions under Section 80C (up to ₹1.5 lakh), 80D (up to ₹25,000 for health insurance), and 80TTA (up to ₹10,000 for savings account interest)."
            suggestions = [
                {"type": "action", "text": "View all tax deductions", "action": "view_tax_deductions"},
                {"type": "action", "text": "Optimize your tax", "action": "optimize_tax"}
            ]
        elif "regime" in keywords:
            response_text = "Based on your current investments and income, the old tax regime is likely more beneficial for you. You can save approximately ₹45,000 in taxes by staying with the old regime."
            suggestions = [
                {"type": "action", "text": "Compare tax regimes", "action": "compare_tax_regimes"},
                {"type": "action", "text": "Calculate tax", "action": "calculate_tax"}
            ]
        else:
            response_text = "I can provide tax advice based on your financial data. Would you like to know about tax deductions, compare tax regimes, or get filing assistance?"
            suggestions = [
                {"type": "action", "text": "Tax deductions", "action": "show_tax_deductions"},
                {"type": "action", "text": "Compare tax regimes", "action": "compare_tax_regimes"},
                {"type": "action", "text": "Filing assistance", "action": "get_filing_assistance"}
            ]
    
    elif query.query_type == "investment_recommendation":
        if "mutual fund" in keywords or "equity" in keywords:
            response_text = "Based on your risk profile, I recommend considering these equity mutual funds: HDFC Index Fund, SBI Blue Chip Fund, and Axis Mid Cap Fund. These funds have shown consistent performance over the last 5 years."
            suggestions = [
                {"type": "action", "text": "See detailed recommendations", "action": "get_mutual_fund_recommendations"},
                {"type": "action", "text": "Compare these funds", "action": "compare_mutual_funds"}
            ]
        elif "tax" in keywords or "saving" in keywords:
            response_text = "For tax-saving investments, you could consider ELSS funds (lock-in of 3 years), PPF (lock-in of 15 years), or NPS (lock-in till retirement). ELSS offers potential for higher returns, while PPF provides guaranteed returns."
            suggestions = [
                {"type": "action", "text": "Compare tax-saving options", "action": "compare_tax_saving_investments"},
                {"type": "action", "text": "Calculate tax savings", "action": "calculate_tax_savings"}
            ]
        else:
            response_text = "I can provide investment recommendations based on your goals and risk profile. Would you like recommendations for wealth creation, tax saving, or retirement planning?"
            suggestions = [
                {"type": "action", "text": "Wealth creation", "action": "get_wealth_creation_recommendations"},
                {"type": "action", "text": "Tax saving", "action": "get_tax_saving_recommendations"},
                {"type": "action", "text": "Retirement planning", "action": "get_retirement_recommendations"}
            ]
    else:
        response_text = "I'm your AI financial assistant. I can help with expense analysis, tax advice, and investment recommendations. What would you like assistance with today?"
        suggestions = [
            {"type": "query", "text": "Analyze my expenses", "query": "expense_analysis"},
            {"type": "query", "text": "Get tax advice", "query": "tax_advice"},
            {"type": "query", "text": "Investment recommendations", "query": "investment_recommendation"}
        ]
    
    # Save conversation to database
    save_conversation(db, query.user_id, query.query_type, query.query_text, response_text)
    
    return AIAssistantResponse(
        response_text=response_text,
        data=data,
        suggestions=suggestions
    )

def extract_keywords(query_text: str) -> List[str]:
    """
    Extract keywords from query text.
    """
    # Simple keyword extraction (in a real app, this would use NLP)
    cleaned_text = query_text.lower()
    words = re.findall(r'\b\w+\b', cleaned_text)
    
    # Filter stop words (simplified version)
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
                 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
                 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
                 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
                 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
                 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
                 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
                 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'}
    
    keywords = [word for word in words if word not in stop_words]
    return keywords

def save_conversation(db: Session, user_id: int, conversation_type: str, query: str, response: str) -> None:
    """
    Save conversation to database.
    """
    db_conversation = AIAssistantConversation(
        user_id=user_id,
        conversation_type=conversation_type,
        query=query,
        response=response
    )
    db.add(db_conversation)
    db.commit()

def get_conversation_history(db: Session, user_id: int, limit: int = 10) -> List[AIAssistantConversation]:
    """
    Get conversation history for a user.
    """
    return db.query(AIAssistantConversation).filter(
        AIAssistantConversation.user_id == user_id
    ).order_by(desc(AIAssistantConversation.created_at)).limit(limit).all()

def analyze_expenses(db: Session, user_id: int, request: ExpenseAnalysisRequest) -> ExpenseAnalysisResponse:
    """
    Analyze user's expense patterns and provide insights.
    """
    # Set default date range if not provided
    end_date = datetime.now() if not request.end_date else request.end_date
    start_date = end_date - timedelta(days=30) if not request.start_date else request.start_date
    
    # Get expense transactions for the period
    expenses_query = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "debit",
        Transaction.transaction_date.between(start_date, end_date)
    )
    
    if request.category_filter:
        category_ids = db.query(TransactionCategory.id).filter(
            TransactionCategory.name.in_(request.category_filter)
        ).all()
        category_ids = [cat_id for (cat_id,) in category_ids]
        expenses_query = expenses_query.filter(Transaction.category_id.in_(category_ids))
    
    expenses = expenses_query.all()
    
    # Calculate total expenses
    total_expenses = sum(float(expense.amount) for expense in expenses)
    
    # Calculate category breakdown
    category_breakdown = defaultdict(float)
    for expense in expenses:
        category_name = "Uncategorized"
        if expense.category:
            category_name = expense.category.name
        category_breakdown[category_name] += float(expense.amount)
    
    # Convert to regular dict
    category_breakdown = dict(category_breakdown)
    
    # Calculate month-over-month change
    previous_start_date = start_date - timedelta(days=30)
    previous_end_date = end_date - timedelta(days=30)
    
    previous_expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == "debit",
        Transaction.transaction_date.between(previous_start_date, previous_end_date)
    ).scalar() or 0
    
    month_over_month_change = 0
    if float(previous_expenses) > 0:
        month_over_month_change = (total_expenses - float(previous_expenses)) / float(previous_expenses) * 100
    
    # Identify top expense categories
    top_categories = [
        {"category": cat, "amount": amount, "percentage": (amount / total_expenses * 100) if total_expenses > 0 else 0}
        for cat, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Identify unusual transactions (simplified approach)
    category_averages = {}
    for cat, total in category_breakdown.items():
        cat_expenses = [e for e in expenses if (e.category and e.category.name == cat) or (not e.category and cat == "Uncategorized")]
        cat_count = len(cat_expenses)
        category_averages[cat] = total / cat_count if cat_count > 0 else 0
    
    unusual_transactions = []
    for expense in expenses:
        cat_name = "Uncategorized" if not expense.category else expense.category.name
        cat_avg = category_averages.get(cat_name, 0)
        
        # If expense is 50% more than category average, flag it
        if cat_avg > 0 and float(expense.amount) > cat_avg * 1.5:
            unusual_transactions.append({
                "id": expense.id,
                "amount": float(expense.amount),
                "description": expense.description,
                "date": expense.transaction_date.isoformat(),
                "category": cat_name,
                "category_average": cat_avg
            })
    
    # Limit to top 5 unusual transactions
    unusual_transactions = sorted(unusual_transactions, key=lambda x: x["amount"], reverse=True)[:5]
    
    # Generate recommendations
    recommendations = []
    
    # Top category spending recommendation
    if top_categories:
        top_cat = top_categories[0]
        recommendations.append(f"Your highest spending category is {top_cat['category']} at ₹{top_cat['amount']:,.2f} ({top_cat['percentage']:.1f}% of total). Consider setting a budget for this category.")
    
    # Month-over-month recommendation
    if month_over_month_change > 10:
        recommendations.append(f"Your spending has increased by {month_over_month_change:.1f}% compared to last month. Review your expenses to identify areas to cut back.")
    elif month_over_month_change < -10:
        recommendations.append(f"Great job! Your spending has decreased by {abs(month_over_month_change):.1f}% compared to last month.")
    
    # Unusual transactions recommendation
    if unusual_transactions:
        recommendations.append(f"You have {len(unusual_transactions)} transactions that are significantly higher than usual for their categories. Review these to ensure they're legitimate.")
    
    # Budget recommendation
    if total_expenses > 0:
        budget_recommendation = f"Based on your spending patterns, a monthly budget of ₹{total_expenses * 0.9:,.2f} would help you save 10% of your current expenses."
        recommendations.append(budget_recommendation)
    
    # Prepare visualization data
    visualization_data = {
        "categories": {
            "labels": list(category_breakdown.keys()),
            "values": list(category_breakdown.values())
        },
        "monthly_trend": []
    }
    
    # Get monthly trend for the last 6 months
    for i in range(5, -1, -1):
        month_start = end_date.replace(day=1) - timedelta(days=i * 30)
        month_end = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
        month_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "debit",
            Transaction.transaction_date.between(month_start, month_end)
        ).scalar() or 0
        
        visualization_data["monthly_trend"].append({
            "month": month_start.strftime("%b %Y"),
            "amount": float(month_expenses)
        })
    
    return ExpenseAnalysisResponse(
        total_expenses=total_expenses,
        category_breakdown=category_breakdown,
        month_over_month_change=month_over_month_change,
        top_expense_categories=top_categories,
        unusual_transactions=unusual_transactions,
        recommendations=recommendations,
        visualization_data=visualization_data
    )

def provide_tax_advice(db: Session, user_id: int, request: TaxAdviceRequest) -> TaxAdviceResponse:
    """
    Provide personalized tax advice.
    """
    # Get user's tax returns for the specified fiscal year
    tax_return = db.query(TaxReturn).filter(
        TaxReturn.user_id == user_id,
        TaxReturn.fiscal_year == request.fiscal_year
    ).first()
    
    # Get tax-deductible transactions for the year
    start_date, end_date = get_fiscal_year_dates(request.fiscal_year)
    
    tax_deductible_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_tax_deductible == True,
        Transaction.transaction_date.between(start_date, end_date)
    ).all()
    
    # Group transactions by tax section
    utilized_deductions = defaultdict(float)
    for txn in tax_deductible_transactions:
        if txn.tax_section:
            utilized_deductions[txn.tax_section] += float(txn.amount)
    
    # Get tax-saving investments if requested
    if request.include_investments:
        tax_saving_investments = db.query(Investment).filter(
            Investment.user_id == user_id,
            Investment.is_tax_saving == True,
            Investment.investment_date.between(start_date, end_date)
        ).all()
        
        for inv in tax_saving_investments:
            if inv.tax_section:
                utilized_deductions[inv.tax_section] += float(inv.initial_amount)
    
    # Create a tax calculator
    calculator = IndianTaxCalculator(fiscal_year=request.fiscal_year)
    
    # Get deduction limits and calculate unused deductions
    unused_deductions = {}
    deduction_limits = {
        "80C": 150000,
        "80D": 25000,  # Basic limit
        "80E": float('inf'),  # No upper limit
        "80G": float('inf'),  # Subject to limits based on donation type
        "80TTA": 10000,
        "80TTB": 50000,
        "HRA": float('inf'),  # Depends on rent paid and salary
        "NPS": 50000,  # Additional NPS deduction under 80CCD(1B)
    }
    
    for section, limit in deduction_limits.items():
        utilized = utilized_deductions.get(section, 0)
        if section in ["80E", "80G", "HRA"]:
            # For sections with no fixed limit
            unused_deductions[section] = "No fixed limit"
        else:
            unused_deductions[section] = max(0, limit - utilized)
    
    # Calculate potential tax savings
    potential_savings = 0
    for section, unused in unused_deductions.items():
        if isinstance(unused, (int, float)):
            # Simple assumption: 30% tax bracket
            potential_savings += unused * 0.3
    
    # Get current tax liability if tax return exists
    current_tax_liability = float(tax_return.tax_payable) if tax_return else 0
    
    # Generate recommendations
    recommendations = []
    
    # 80C recommendation
    if "80C" in unused_deductions and isinstance(unused_deductions["80C"], (int, float)) and unused_deductions["80C"] > 0:
        recommendations.append({
            "section": "80C",
            "description": "You have ₹{:,.2f} unused deduction limit under Section 80C".format(unused_deductions["80C"]),
            "action": "Consider investing in ELSS, PPF, NSC, or 5-year tax-saving FDs",
            "potential_savings": unused_deductions["80C"] * 0.3
        })
    
    # 80D recommendation
    if "80D" in unused_deductions and isinstance(unused_deductions["80D"], (int, float)) and unused_deductions["80D"] > 0:
        recommendations.append({
            "section": "80D",
            "description": "You have ₹{:,.2f} unused deduction limit under Section 80D for health insurance".format(unused_deductions["80D"]),
            "action": "Consider getting health insurance for yourself and your family",
            "potential_savings": unused_deductions["80D"] * 0.3
        })
    
    # NPS recommendation
    if "NPS" in unused_deductions and isinstance(unused_deductions["NPS"], (int, float)) and unused_deductions["NPS"] > 0:
        recommendations.append({
            "section": "80CCD(1B)",
            "description": "You have ₹{:,.2f} unused deduction limit for additional NPS contribution".format(unused_deductions["NPS"]),
            "action": "Consider investing in National Pension System for an additional tax deduction",
            "potential_savings": unused_deductions["NPS"] * 0.3
        })
    
    # Add deadline reminders
    today = datetime.now().date()
    fiscal_year_end = end_date.date()
    days_to_fiscal_end = (fiscal_year_end - today).days
    
    deadline_reminders = []
    
    if days_to_fiscal_end > 0:
        deadline_reminders.append({
            "description": f"You have {days_to_fiscal_end} days left to make tax-saving investments for the current fiscal year",
            "date": fiscal_year_end.isoformat(),
            "type": "investment_deadline"
        })
    
    # Add ITR filing deadline (usually July 31st for individuals)
    itr_deadline = datetime(year=fiscal_year_end.year, month=7, day=31).date()
    if today <= itr_deadline:
        days_to_itr_deadline = (itr_deadline - today).days
        deadline_reminders.append({
            "description": f"You have {days_to_itr_deadline} days left to file your Income Tax Return",
            "date": itr_deadline.isoformat(),
            "type": "itr_filing_deadline"
        })
    
    return TaxAdviceResponse(
        current_tax_liability=current_tax_liability,
        potential_savings=potential_savings,
        utilized_deductions=dict(utilized_deductions),
        unused_deductions={k: v for k, v in unused_deductions.items() if isinstance(v, (int, float))},
        recommendations=recommendations,
        deadline_reminders=deadline_reminders
    )

def get_fiscal_year_dates(fiscal_year: str) -> tuple:
    """
    Convert a fiscal year string (e.g., "2023-24") to start and end dates.
    """
    parts = fiscal_year.split("-")
    start_year = int("20" + parts[0]) if len(parts[0]) == 2 else int(parts[0])
    end_year = start_year + 1
    
    start_date = datetime(start_year, 4, 1)
    end_date = datetime(end_year, 3, 31, 23, 59, 59)
    
    return start_date, end_date

def recommend_investments(db: Session, user_id: int, request: InvestmentRecommendationRequest) -> InvestmentRecommendationResponse:
    """
    Get personalized investment recommendations.
    """
    # Get user's existing investments
    investments = db.query(Investment).filter(
        Investment.user_id == user_id,
        Investment.is_active == True
    ).all()
    
    # Determine the user's risk profile if not provided
    risk_profile = request.risk_profile
    if not risk_profile:
        if investments:
            # Analyze existing investments to determine risk profile
            high_risk_count = sum(1 for inv in investments if inv.investment_type and inv.investment_type.risk_level == "high")
            medium_risk_count = sum(1 for inv in investments if inv.investment_type and inv.investment_type.risk_level == "medium")
            low_risk_count = sum(1 for inv in investments if inv.investment_type and inv.investment_type.risk_level == "low")
            
            total_investments = len(investments)
            if total_investments > 0:
                if high_risk_count / total_investments > 0.5:
                    risk_profile = "high"
                elif medium_risk_count / total_investments > 0.5:
                    risk_profile = "medium"
                else:
                    risk_profile = "low"
            else:
                risk_profile = "medium"  # Default
        else:
            risk_profile = "medium"  # Default if no existing investments
    
    # Get available investment types
    investment_types = db.query(InvestmentType).all()
    
    # Filter types based on risk profile and tax saving focus
    suitable_types = []
    for inv_type in investment_types:
        if inv_type.risk_level == risk_profile or (
            risk_profile == "high" and inv_type.risk_level == "medium"
        ) or (
            risk_profile == "low" and inv_type.risk_level == "medium"
        ):
            if not request.tax_saving_focus or inv_type.is_tax_saving:
                suitable_types.append(inv_type)
    
    # If no suitable types found, use all types
    if not suitable_types:
        suitable_types = investment_types
    
    # Generate recommendations
    recommendations = []
    for inv_type in suitable_types[:5]:  # Limit to 5 recommendations
        recommendations.append({
            "name": inv_type.name,
            "type": inv_type.name,
            "description": inv_type.description or f"{inv_type.name} investment",
            "risk_level": inv_type.risk_level,
            "expected_returns": inv_type.expected_returns or "Varies",
            "min_investment": float(inv_type.min_investment) if inv_type.min_investment else 0,
            "lock_in_period": inv_type.lock_in_period if inv_type.lock_in_period else 0,
            "is_tax_saving": inv_type.is_tax_saving,
            "tax_section": inv_type.tax_section,
            "recommended_amount": calculate_recommended_amount(request.monthly_investment_capacity, inv_type)
        })
    
    # Calculate expected returns (simplified)
    expected_returns = {}
    if risk_profile == "high":
        expected_returns = {
            "1_year": 12.0,
            "3_year": 14.0,
            "5_year": 16.0
        }
    elif risk_profile == "medium":
        expected_returns = {
            "1_year": 8.0,
            "3_year": 10.0,
            "5_year": 12.0
        }
    else:  # low
        expected_returns = {
            "1_year": 5.0,
            "3_year": 6.0,
            "5_year": 7.0
        }
    
    # Calculate tax benefits
    tax_benefits = {}
    if request.tax_saving_focus:
        for inv_type in suitable_types:
            if inv_type.is_tax_saving and inv_type.tax_section:
                # Simple calculation: assume 30% tax slab
                amount = min(
                    request.monthly_investment_capacity * 12 if request.monthly_investment_capacity else 150000,
                    get_section_limit(inv_type.tax_section)
                )
                tax_benefits[inv_type.tax_section] = amount * 0.3
    
    # Calculate recommended asset allocation
    recommended_allocation = {}
    if risk_profile == "high":
        recommended_allocation = {
            "Equity": 70,
            "Debt": 20,
            "Gold": 5,
            "Alternative Investments": 5
        }
    elif risk_profile == "medium":
        recommended_allocation = {
            "Equity": 50,
            "Debt": 40,
            "Gold": 5,
            "Alternative Investments": 5
        }
    else:  # low
        recommended_allocation = {
            "Equity": 30,
            "Debt": 60,
            "Gold": 10,
            "Alternative Investments": 0
        }
    
    return InvestmentRecommendationResponse(
        recommendations=recommendations,
        expected_returns=expected_returns,
        risk_assessment=get_risk_assessment(risk_profile),
        tax_benefits=tax_benefits,
        recommended_allocation=recommended_allocation
    )

def calculate_recommended_amount(monthly_capacity: Optional[float], investment_type: InvestmentType) -> float:
    """
    Calculate recommended investment amount based on capacity and type.
    """
    if not monthly_capacity:
        return float(investment_type.min_investment) if investment_type.min_investment else 5000
    
    # Different allocation percentages based on risk level
    allocation_percentage = 0.3  # Default 30%
    if investment_type.risk_level == "high":
        allocation_percentage = 0.4  # 40% for high risk
    elif investment_type.risk_level == "low":
        allocation_percentage = 0.2  # 20% for low risk
    
    # For tax-saving investments, use higher allocation
    if investment_type.is_tax_saving:
        allocation_percentage += 0.1
    
    recommended = monthly_capacity * allocation_percentage
    
    # Ensure minimum investment amount
    if investment_type.min_investment and recommended < float(investment_type.min_investment):
        recommended = float(investment_type.min_investment)
    
    return recommended

def get_risk_assessment(risk_profile: str) -> str:
    """
    Get risk assessment description based on risk profile.
    """
    if risk_profile == "high":
        return "Your risk profile suggests you can tolerate significant market volatility for potentially higher returns. Focus on growth-oriented investments with a long-term horizon."
    elif risk_profile == "medium":
        return "Your balanced risk profile suggests a mix of growth and stability. Consider a diversified portfolio with moderate exposure to market fluctuations."
    else:  # low
        return "Your conservative risk profile suggests prioritizing capital preservation and steady income. Focus on stable investments with consistent returns and lower volatility."

def get_section_limit(section: str) -> float:
    """
    Get the deduction limit for a tax section.
    """
    limits = {
        "80C": 150000,
        "80CCD(1B)": 50000,
        "80D": 25000,
        "80TTA": 10000,
        "80TTB": 50000,
        "80E": float('inf'),  # No limit
        "80G": float('inf')   # Depends on donation type
    }
    return limits.get(section, 0)