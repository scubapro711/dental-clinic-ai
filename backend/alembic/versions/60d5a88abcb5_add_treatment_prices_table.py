"""add_treatment_prices_table

Revision ID: 60d5a88abcb5
Revises: f9f7d794e9ed
Create Date: 2025-10-07 20:49:45.577109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '60d5a88abcb5'
down_revision: Union[str, Sequence[str], None] = 'f9f7d794e9ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create treatment_prices table
    op.create_table(
        'treatment_prices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        
        # Treatment identification
        sa.Column('treatment_code', sa.String(50), nullable=False),
        sa.Column('treatment_name_hebrew', sa.String(255), nullable=False),
        sa.Column('treatment_name_english', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Pricing
        sa.Column('base_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('member_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('insurance_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='ILS'),
        
        # Duration and scheduling
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('requires_specialist', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('specialist_type', sa.String(100), nullable=True),
        
        # Odoo integration
        sa.Column('odoo_product_id', sa.Integer(), nullable=True),
        sa.Column('odoo_product_template_id', sa.Integer(), nullable=True),
        
        # Status and visibility
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_visible_online', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='false'),
        
        # Metadata
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'treatment_code', name='uq_org_treatment_code')
    )
    
    # Create indexes for performance
    op.create_index('ix_treatment_prices_org', 'treatment_prices', ['organization_id'])
    op.create_index('ix_treatment_prices_code', 'treatment_prices', ['treatment_code'])
    op.create_index('ix_treatment_prices_category', 'treatment_prices', ['category'])
    op.create_index('ix_treatment_prices_odoo_product', 'treatment_prices', ['odoo_product_id'])
    op.create_index('ix_treatment_prices_active', 'treatment_prices', ['is_active'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_treatment_prices_active', table_name='treatment_prices')
    op.drop_index('ix_treatment_prices_odoo_product', table_name='treatment_prices')
    op.drop_index('ix_treatment_prices_category', table_name='treatment_prices')
    op.drop_index('ix_treatment_prices_code', table_name='treatment_prices')
    op.drop_index('ix_treatment_prices_org', table_name='treatment_prices')
    
    # Drop table
    op.drop_table('treatment_prices')
