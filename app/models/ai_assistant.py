# app/models/ai_assistant.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AIAssistantQuery(BaseModel):
    query_type: str  # expense_analysis, tax_advice, investment_recommendation
    user_id: int
    query_text: str
    context_data: Optional[Dict[str, Any]] = None

class AIAssistantResponse(BaseModel):
    response_text: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = datetime.now()

class ExpenseAnalysisRequest(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category_filter: Optional[List[str]] = None

class ExpenseAnalysisResponse(BaseModel):
    total_expenses: float
    category_breakdown: Dict[str, float]
    month_over_month_change: float
    top_expense_categories: List[Dict[str, Any]]
    unusual_transactions: List[Dict[str, Any]]
    recommendations: List[str]
    visualization_data: Dict[str, Any]

class TaxAdviceRequest(BaseModel):
    fiscal_year: str
    include_investments: bool = True

class TaxAdviceResponse(BaseModel):
    current_tax_liability: float
    potential_savings: float
    utilized_deductions: Dict[str, float]
    unused_deductions: Dict[str, float]
    recommendations: List[Dict[str, Any]]
    deadline_reminders: List[Dict[str, Any]]

class InvestmentRecommendationRequest(BaseModel):
    risk_profile: Optional[str] = None  # low, medium, high
    investment_horizon: Optional[int] = None  # in months
    tax_saving_focus: bool = False
    monthly_investment_capacity: Optional[float] = None

class InvestmentRecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    expected_returns: Dict[str, float]
    risk_assessment: str
    tax_benefits: Dict[str, float]
    recommended_allocation: Dict[str, float]