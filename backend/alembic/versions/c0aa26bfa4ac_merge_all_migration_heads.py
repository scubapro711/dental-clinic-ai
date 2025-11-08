"""merge_all_migration_heads

Revision ID: c0aa26bfa4ac
Revises: add_pilot_apps, f1a2b3c4d5e6
Create Date: 2025-11-08 10:52:09.559900

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0aa26bfa4ac'
down_revision: Union[str, Sequence[str], None] = ('add_pilot_apps', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
