"""create_user_patient_mappings_table

Revision ID: d00785b0bf20
Revises: ec4c34014113
Create Date: 2025-10-10 21:14:41.621472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd00785b0bf20'
down_revision: Union[str, Sequence[str], None] = 'ec4c34014113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_patient_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('odoo_patient_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_id_active', 'user_patient_mappings', ['user_id', 'is_active'])
    op.create_index('idx_odoo_patient_id_active', 'user_patient_mappings', ['odoo_patient_id', 'is_active'])
    op.create_index('idx_email_active', 'user_patient_mappings', ['email', 'is_active'])
    op.create_index(op.f('ix_user_patient_mappings_user_id'), 'user_patient_mappings', ['user_id'], unique=True)
    op.create_index(op.f('ix_user_patient_mappings_odoo_patient_id'), 'user_patient_mappings', ['odoo_patient_id'], unique=False)
    op.create_index(op.f('ix_user_patient_mappings_email'), 'user_patient_mappings', ['email'], unique=False)
    op.create_index(op.f('ix_user_patient_mappings_id'), 'user_patient_mappings', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_patient_mappings_id'), table_name='user_patient_mappings')
    op.drop_index(op.f('ix_user_patient_mappings_email'), table_name='user_patient_mappings')
    op.drop_index(op.f('ix_user_patient_mappings_odoo_patient_id'), table_name='user_patient_mappings')
    op.drop_index(op.f('ix_user_patient_mappings_user_id'), table_name='user_patient_mappings')
    op.drop_index('idx_email_active', table_name='user_patient_mappings')
    op.drop_index('idx_odoo_patient_id_active', table_name='user_patient_mappings')
    op.drop_index('idx_user_id_active', table_name='user_patient_mappings')
    op.drop_table('user_patient_mappings')
