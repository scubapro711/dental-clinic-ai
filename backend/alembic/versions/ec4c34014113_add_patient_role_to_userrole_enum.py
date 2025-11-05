"""add_patient_role_to_userrole_enum

Revision ID: ec4c34014113
Revises: e47ec69deedc
Create Date: 2025-10-10 21:00:23.948418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec4c34014113'
down_revision: Union[str, Sequence[str], None] = 'telegram_messages_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add PATIENT to UserRole enum."""
    # Add PATIENT to the userrole enum
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'PATIENT'")


def downgrade() -> None:
    """Downgrade schema - Cannot remove enum values in PostgreSQL."""
    # PostgreSQL doesn't support removing enum values
    # This is a one-way migration
    pass
