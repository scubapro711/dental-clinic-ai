"""add_mfa_backup_codes_column_to_users

Revision ID: 5a8c2b9d3e4f
Revises: 4f9f41a55558
Create Date: 2025-11-04 07:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a8c2b9d3e4f'
down_revision: Union[str, Sequence[str], None] = '4f9f41a55558'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing mfa_backup_codes column to users table.
    
    Note: mfa_enabled and mfa_secret already exist from initial migration.
    This migration only adds the missing mfa_backup_codes column.
    """
    # Add mfa_backup_codes column (the only missing MFA column)
    op.add_column('users', sa.Column('mfa_backup_codes', sa.String(length=1000), nullable=True))


def downgrade() -> None:
    """Remove mfa_backup_codes column from users table."""
    op.drop_column('users', 'mfa_backup_codes')
