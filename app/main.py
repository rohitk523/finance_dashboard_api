# app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import auth, transactions, investments, tax, ai_assistant
from app.config import settings
from app.database.db import Base, engine

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"],
)
app.include_router(
    transactions.router,
    prefix=f"{settings.API_V1_STR}/transactions",
    tags=["transactions"],
)
app.include_router(
    investments.router,
    prefix=f"{settings.API_V1_STR}/investments",
    tags=["investments"],
)
app.include_router(
    tax.router,
    prefix=f"{settings.API_V1_STR}/tax",
    tags=["tax"],
)
app.include_router(
    ai_assistant.router,
    prefix=f"{settings.API_V1_STR}/ai",
    tags=["ai-assistant"],
)

@app.get("/")
def root():
    return {"message": "Welcome to Indian Finance Dashboard API"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)