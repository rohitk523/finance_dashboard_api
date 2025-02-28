"""Initial migration

Revision ID: 99a421d448f8
Revises: 
Create Date: 2025-02-28 11:09:10.819406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99a421d448f8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('investment_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('risk_level', sa.String(length=50), nullable=True),
    sa.Column('min_investment', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('expected_returns', sa.String(length=50), nullable=True),
    sa.Column('tax_implication', sa.Text(), nullable=True),
    sa.Column('is_tax_saving', sa.Boolean(), nullable=True),
    sa.Column('tax_section', sa.String(length=10), nullable=True),
    sa.Column('lock_in_period', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investment_types_id'), 'investment_types', ['id'], unique=False)
    op.create_table('transaction_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category_type', sa.String(length=50), nullable=False),
    sa.Column('is_tax_deductible', sa.Boolean(), nullable=True),
    sa.Column('tax_section', sa.String(length=10), nullable=True),
    sa.Column('icon', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transaction_categories_id'), 'transaction_categories', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=15), nullable=True),
    sa.Column('pan_number', sa.String(length=10), nullable=True),
    sa.Column('aadhar_number', sa.String(length=12), nullable=True),
    sa.Column('date_of_birth', sa.Date(), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('profile_image_url', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('aadhar_number'),
    sa.UniqueConstraint('pan_number')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('ai_assistant_conversations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('conversation_type', sa.String(length=50), nullable=False),
    sa.Column('query', sa.Text(), nullable=False),
    sa.Column('response', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_assistant_conversations_id'), 'ai_assistant_conversations', ['id'], unique=False)
    op.create_table('auth_tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=255), nullable=False),
    sa.Column('token_type', sa.String(length=50), nullable=False),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_tokens_id'), 'auth_tokens', ['id'], unique=False)
    op.create_table('bank_accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('account_name', sa.String(length=100), nullable=False),
    sa.Column('bank_name', sa.String(length=100), nullable=False),
    sa.Column('account_number', sa.String(length=30), nullable=False),
    sa.Column('ifsc_code', sa.String(length=11), nullable=True),
    sa.Column('account_type', sa.String(length=50), nullable=True),
    sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_id'), 'bank_accounts', ['id'], unique=False)
    op.create_table('documents',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('document_type', sa.String(length=50), nullable=False),
    sa.Column('document_name', sa.String(length=255), nullable=False),
    sa.Column('file_path', sa.String(length=255), nullable=False),
    sa.Column('file_size', sa.Integer(), nullable=False),
    sa.Column('mime_type', sa.String(length=100), nullable=False),
    sa.Column('upload_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('fiscal_year', sa.String(length=9), nullable=True),
    sa.Column('related_entity_type', sa.String(length=50), nullable=True),
    sa.Column('related_entity_id', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_table('investments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('investment_type_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('investment_date', sa.Date(), nullable=False),
    sa.Column('initial_amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('current_value', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('units', sa.Numeric(precision=15, scale=6), nullable=True),
    sa.Column('maturity_date', sa.Date(), nullable=True),
    sa.Column('interest_rate', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('broker', sa.String(length=100), nullable=True),
    sa.Column('folio_number', sa.String(length=100), nullable=True),
    sa.Column('is_tax_saving', sa.Boolean(), nullable=True),
    sa.Column('tax_section', sa.String(length=10), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['investment_type_id'], ['investment_types.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investments_id'), 'investments', ['id'], unique=False)
    op.create_table('tax_returns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('fiscal_year', sa.String(length=9), nullable=False),
    sa.Column('itr_form_type', sa.String(length=10), nullable=False),
    sa.Column('filing_status', sa.String(length=50), nullable=False),
    sa.Column('gross_total_income', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('total_deductions', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('taxable_income', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('tax_payable', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('tds_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('tax_paid', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('refund_amount', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('refund_status', sa.String(length=50), nullable=True),
    sa.Column('filing_date', sa.Date(), nullable=True),
    sa.Column('acknowledgment_number', sa.String(length=100), nullable=True),
    sa.Column('verification_method', sa.String(length=50), nullable=True),
    sa.Column('verification_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tax_returns_id'), 'tax_returns', ['id'], unique=False)
    op.create_table('user_preferences',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('notification_enabled', sa.Boolean(), nullable=True),
    sa.Column('dashboard_customization', sa.Text(), nullable=True),
    sa.Column('default_view', sa.String(length=50), nullable=True),
    sa.Column('preferred_language', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('investment_transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('investment_id', sa.Integer(), nullable=False),
    sa.Column('transaction_date', sa.Date(), nullable=False),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('units', sa.Numeric(precision=15, scale=6), nullable=True),
    sa.Column('unit_price', sa.Numeric(precision=15, scale=2), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['investment_id'], ['investments.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investment_transactions_id'), 'investment_transactions', ['id'], unique=False)
    op.create_table('tax_deductions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tax_return_id', sa.Integer(), nullable=False),
    sa.Column('section', sa.String(length=10), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('proof_document_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['proof_document_id'], ['documents.id'], ),
    sa.ForeignKeyConstraint(['tax_return_id'], ['tax_returns.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tax_deductions_id'), 'tax_deductions', ['id'], unique=False)
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('payment_method', sa.String(length=50), nullable=True),
    sa.Column('upi_id', sa.String(length=100), nullable=True),
    sa.Column('bank_account_id', sa.Integer(), nullable=True),
    sa.Column('is_recurring', sa.Boolean(), nullable=True),
    sa.Column('recurring_frequency', sa.String(length=50), nullable=True),
    sa.Column('is_tax_deductible', sa.Boolean(), nullable=True),
    sa.Column('tax_section', sa.String(length=10), nullable=True),
    sa.Column('receipt_url', sa.String(length=255), nullable=True),
    sa.Column('gst_applicable', sa.Boolean(), nullable=True),
    sa.Column('gst_amount', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('hsn_sac_code', sa.String(length=20), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['bank_account_id'], ['bank_accounts.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['transaction_categories.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_tax_deductions_id'), table_name='tax_deductions')
    op.drop_table('tax_deductions')
    op.drop_index(op.f('ix_investment_transactions_id'), table_name='investment_transactions')
    op.drop_table('investment_transactions')
    op.drop_table('user_preferences')
    op.drop_index(op.f('ix_tax_returns_id'), table_name='tax_returns')
    op.drop_table('tax_returns')
    op.drop_index(op.f('ix_investments_id'), table_name='investments')
    op.drop_table('investments')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    op.drop_index(op.f('ix_bank_accounts_id'), table_name='bank_accounts')
    op.drop_table('bank_accounts')
    op.drop_index(op.f('ix_auth_tokens_id'), table_name='auth_tokens')
    op.drop_table('auth_tokens')
    op.drop_index(op.f('ix_ai_assistant_conversations_id'), table_name='ai_assistant_conversations')
    op.drop_table('ai_assistant_conversations')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_transaction_categories_id'), table_name='transaction_categories')
    op.drop_table('transaction_categories')
    op.drop_index(op.f('ix_investment_types_id'), table_name='investment_types')
    op.drop_table('investment_types')
    # ### end Alembic commands ###
