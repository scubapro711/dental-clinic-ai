"""add_clinic_settings_table

Revision ID: f9f7d794e9ed
Revises: 96fa5e3cb6a3
Create Date: 2025-10-07 20:45:30.054206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9f7d794e9ed'
down_revision: Union[str, Sequence[str], None] = '96fa5e3cb6a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create clinic_settings table
    op.create_table(
        'clinic_settings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        
        # Operating hours (based on Israeli clinic research)
        sa.Column('sunday_open', sa.Time(), nullable=True),
        sa.Column('sunday_close', sa.Time(), nullable=True),
        sa.Column('monday_open', sa.Time(), nullable=True),
        sa.Column('monday_close', sa.Time(), nullable=True),
        sa.Column('tuesday_open', sa.Time(), nullable=True),
        sa.Column('tuesday_close', sa.Time(), nullable=True),
        sa.Column('wednesday_open', sa.Time(), nullable=True),
        sa.Column('wednesday_close', sa.Time(), nullable=True),
        sa.Column('thursday_open', sa.Time(), nullable=True),
        sa.Column('thursday_close', sa.Time(), nullable=True),
        sa.Column('friday_open', sa.Time(), nullable=True),
        sa.Column('friday_close', sa.Time(), nullable=True),
        sa.Column('saturday_open', sa.Time(), nullable=True),
        sa.Column('saturday_close', sa.Time(), nullable=True),
        
        # Appointment settings (from DENTAL_CLINIC_OPERATIONS_RESEARCH.md)
        sa.Column('default_appointment_duration', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('buffer_between_appointments', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('advance_booking_days', sa.Integer(), nullable=False, server_default='60'),
        sa.Column('cancellation_notice_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('no_show_fee', sa.Numeric(10, 2), nullable=False, server_default='100.00'),
        sa.Column('allow_online_booking', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('require_deposit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deposit_amount', sa.Numeric(10, 2), nullable=True),
        
        # Communication settings
        sa.Column('sms_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('whatsapp_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('telegram_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reminder_hours_before', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('send_followup_after_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('send_recall_after_months', sa.Integer(), nullable=False, server_default='6'),
        
        # Billing settings (Israeli market)
        sa.Column('currency', sa.String(3), nullable=False, server_default='ILS'),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='17.00'),
        sa.Column('payment_methods', sa.JSON(), nullable=False, server_default='["cash", "credit_card", "bank_transfer", "bit"]'),
        sa.Column('invoice_prefix', sa.String(10), nullable=True),
        sa.Column('invoice_starting_number', sa.Integer(), nullable=False, server_default='1000'),
        
        # Clinic information
        sa.Column('clinic_name_hebrew', sa.String(255), nullable=True),
        sa.Column('clinic_name_english', sa.String(255), nullable=True),
        sa.Column('clinic_logo_url', sa.String(500), nullable=True),
        sa.Column('clinic_address', sa.Text(), nullable=True),
        sa.Column('clinic_phone', sa.String(20), nullable=True),
        sa.Column('clinic_email', sa.String(255), nullable=True),
        sa.Column('clinic_website', sa.String(255), nullable=True),
        
        # Business settings
        sa.Column('business_license_number', sa.String(50), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', name='uq_clinic_settings_org')
    )
    
    # Create index for performance
    op.create_index('ix_clinic_settings_org', 'clinic_settings', ['organization_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_clinic_settings_org', table_name='clinic_settings')
    
    # Drop table
    op.drop_table('clinic_settings')
