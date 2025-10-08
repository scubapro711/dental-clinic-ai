"""add cognito_sub to users

Revision ID: a1b2c3d4e5f6
Revises: 60d5a88abcb5
Create Date: 2025-10-08 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '60d5a88abcb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add cognito_sub column to users table
    op.add_column('users', sa.Column('cognito_sub', sa.String(255), nullable=True))
    
    # Add unique index on cognito_sub
    op.create_index('ix_users_cognito_sub', 'users', ['cognito_sub'], unique=True)
    
    # Add email_verified column
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_users_cognito_sub', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'cognito_sub')
    op.drop_column('users', 'email_verified')
