"""create user_patient_mapping table

Revision ID: 001_user_patient_mapping
Revises: 
Create Date: 2025-10-10 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '001_user_patient_mapping'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create user_patient_mappings table."""
    op.create_table(
        'user_patient_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('odoo_patient_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=func.now()),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_id', 'user_patient_mappings', ['user_id'], unique=True)
    op.create_index('idx_odoo_patient_id', 'user_patient_mappings', ['odoo_patient_id'])
    op.create_index('idx_email', 'user_patient_mappings', ['email'])
    op.create_index('idx_user_id_active', 'user_patient_mappings', ['user_id', 'is_active'])
    op.create_index('idx_odoo_patient_id_active', 'user_patient_mappings', ['odoo_patient_id', 'is_active'])
    op.create_index('idx_email_active', 'user_patient_mappings', ['email', 'is_active'])


def downgrade():
    """Drop user_patient_mappings table."""
    op.drop_index('idx_email_active', table_name='user_patient_mappings')
    op.drop_index('idx_odoo_patient_id_active', table_name='user_patient_mappings')
    op.drop_index('idx_user_id_active', table_name='user_patient_mappings')
    op.drop_index('idx_email', table_name='user_patient_mappings')
    op.drop_index('idx_odoo_patient_id', table_name='user_patient_mappings')
    op.drop_index('idx_user_id', table_name='user_patient_mappings')
    op.drop_table('user_patient_mappings')

