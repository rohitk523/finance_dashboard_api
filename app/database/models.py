# app/database/models.py
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Text, Date, DateTime, Enum, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.tax import ITRFormType, FilingStatus, DocumentType

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(15))
    pan_number = Column(String(10), unique=True)
    aadhar_number = Column(String(12), unique=True)
    date_of_birth = Column(Date)
    address = Column(Text)
    profile_image_url = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    preferences = relationship("UserPreference", uselist=False, back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    bank_accounts = relationship("BankAccount", back_populates="user", cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    tax_returns = relationship("TaxReturn", back_populates="user", cascade="all, delete-orphan")
    ai_conversations = relationship("AIAssistantConversation", back_populates="user", cascade="all, delete-orphan")
    auth_tokens = relationship("AuthToken", back_populates="user", cascade="all, delete-orphan")


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    notification_enabled = Column(Boolean, default=True)
    dashboard_customization = Column(Text)  # Storing JSON as text
    default_view = Column(String(50), default="dashboard")
    preferred_language = Column(String(50), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="preferences")


class TransactionCategory(Base):
    __tablename__ = "transaction_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category_type = Column(String(50), nullable=False)  # income, expense, investment
    is_tax_deductible = Column(Boolean, default=False)
    tax_section = Column(String(10))
    icon = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    description = Column(Text)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    category_id = Column(Integer, ForeignKey("transaction_categories.id"))
    transaction_type = Column(String(50), nullable=False)  # debit, credit
    payment_method = Column(String(50))
    upi_id = Column(String(100))
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"))
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(50))
    is_tax_deductible = Column(Boolean, default=False)
    tax_section = Column(String(10))
    receipt_url = Column(String(255))
    gst_applicable = Column(Boolean, default=False)
    gst_amount = Column(Numeric(10, 2))
    hsn_sac_code = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("TransactionCategory", back_populates="transactions")
    bank_account = relationship("BankAccount", back_populates="transactions")


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    account_name = Column(String(100), nullable=False)
    bank_name = Column(String(100), nullable=False)
    account_number = Column(String(30), nullable=False)
    ifsc_code = Column(String(11))
    account_type = Column(String(50))
    balance = Column(Numeric(15, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bank_accounts")
    transactions = relationship("Transaction", back_populates="bank_account")


class InvestmentType(Base):
    __tablename__ = "investment_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    risk_level = Column(String(50))
    min_investment = Column(Numeric(15, 2))
    expected_returns = Column(String(50))
    tax_implication = Column(Text)
    is_tax_saving = Column(Boolean, default=False)
    tax_section = Column(String(10))
    lock_in_period = Column(Integer)  # in months
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    investments = relationship("Investment", back_populates="investment_type")


class Investment(Base):
    __tablename__ = "investments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    investment_type_id = Column(Integer, ForeignKey("investment_types.id"), nullable=False)
    name = Column(String(255), nullable=False)
    investment_date = Column(Date, nullable=False)
    initial_amount = Column(Numeric(15, 2), nullable=False)
    current_value = Column(Numeric(15, 2))
    units = Column(Numeric(15, 6))
    maturity_date = Column(Date)
    interest_rate = Column(Numeric(5, 2))
    broker = Column(String(100))
    folio_number = Column(String(100))
    is_tax_saving = Column(Boolean, default=False)
    tax_section = Column(String(10))
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="investments")
    investment_type = relationship("InvestmentType", back_populates="investments")
    transactions = relationship("InvestmentTransaction", back_populates="investment", cascade="all, delete-orphan")


class InvestmentTransaction(Base):
    __tablename__ = "investment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # buy, sell, dividend, interest
    amount = Column(Numeric(15, 2), nullable=False)
    units = Column(Numeric(15, 6))
    unit_price = Column(Numeric(15, 2))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    investment = relationship("Investment", back_populates="transactions")


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(50), nullable=False)  # Enum as string: income_proof, tax_form, etc.
    document_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    fiscal_year = Column(String(9))  # 2023-24
    related_entity_type = Column(String(50))  # tax_return, transaction, investment
    related_entity_id = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
    tax_deductions = relationship("TaxDeduction", back_populates="proof_document")


class TaxReturn(Base):
    __tablename__ = "tax_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    fiscal_year = Column(String(9), nullable=False)  # 2023-24
    itr_form_type = Column(String(10), nullable=False)  # ITR-1, ITR-2, etc.
    filing_status = Column(String(50), nullable=False, default="draft")  # draft, filed, verified
    gross_total_income = Column(Numeric(15, 2))
    total_deductions = Column(Numeric(15, 2))
    taxable_income = Column(Numeric(15, 2))
    tax_payable = Column(Numeric(15, 2))
    tds_amount = Column(Numeric(15, 2))
    tax_paid = Column(Numeric(15, 2))
    refund_amount = Column(Numeric(15, 2))
    refund_status = Column(String(50))
    filing_date = Column(Date)
    acknowledgment_number = Column(String(100))
    verification_method = Column(String(50))
    verification_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tax_returns")
    deductions = relationship("TaxDeduction", back_populates="tax_return", cascade="all, delete-orphan")


class TaxDeduction(Base):
    __tablename__ = "tax_deductions"
    
    id = Column(Integer, primary_key=True, index=True)
    tax_return_id = Column(Integer, ForeignKey("tax_returns.id", ondelete="CASCADE"), nullable=False)
    section = Column(String(10), nullable=False)  # 80C, 80D, etc.
    description = Column(Text, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    proof_document_id = Column(Integer, ForeignKey("documents.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tax_return = relationship("TaxReturn", back_populates="deductions")
    proof_document = relationship("Document", back_populates="tax_deductions")


class AIAssistantConversation(Base):
    __tablename__ = "ai_assistant_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    conversation_type = Column(String(50), nullable=False)  # expense_analysis, tax_advice, investment_recommendation
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="ai_conversations")


class AuthToken(Base):
    __tablename__ = "auth_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), nullable=False)
    token_type = Column(String(50), nullable=False)  # refresh, reset_password, verification
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="auth_tokens")