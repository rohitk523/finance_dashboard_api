# app/api/routes/ai_assistant.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_active_user
from app.database.db import get_db
from app.database.models import User
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
from app.services.ai_assistant import (
    process_assistant_query,
    get_conversation_history,
    analyze_expenses,
    provide_tax_advice,
    recommend_investments
)

router = APIRouter()

@router.post("/assistant", response_model=AIAssistantResponse)
def query_assistant(
    query: AIAssistantQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Send a general query to the AI assistant.
    """
    # Override the user_id from the authenticated user
    query.user_id = current_user.id
    return process_assistant_query(db=db, query=query)


@router.get("/assistant/history", response_model=List[AIAssistantResponse])
def get_assistant_history(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get conversation history with the AI assistant.
    """
    return get_conversation_history(db=db, user_id=current_user.id, limit=limit)


@router.post("/assistant/analyze-expenses", response_model=ExpenseAnalysisResponse)
def analyze_user_expenses(
    request: ExpenseAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Analyze user's expense patterns and provide insights.
    """
    return analyze_expenses(db=db, user_id=current_user.id, request=request)


@router.post("/assistant/tax-advice", response_model=TaxAdviceResponse)
def get_tax_advice(
    request: TaxAdviceRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get personalized tax advice from the AI assistant.
    """
    return provide_tax_advice(db=db, user_id=current_user.id, request=request)


@router.post("/assistant/investment-recommendations", response_model=InvestmentRecommendationResponse)
def get_investment_recommendations(
    request: InvestmentRecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Get personalized investment recommendations from the AI assistant.
    """
    return recommend_investments(db=db, user_id=current_user.id, request=request)