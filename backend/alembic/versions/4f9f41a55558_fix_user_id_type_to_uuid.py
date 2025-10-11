"""fix_user_id_type_to_uuid

Revision ID: 4f9f41a55558
Revises: d00785b0bf20
Create Date: 2025-10-10 21:15:52.451052

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f9f41a55558'
down_revision: Union[str, Sequence[str], None] = 'd00785b0bf20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change user_id column from VARCHAR to UUID
    op.execute("ALTER TABLE user_patient_mappings ALTER COLUMN user_id TYPE UUID USING user_id::uuid")


def downgrade() -> None:
    """Downgrade schema."""
    # Change user_id column back from UUID to VARCHAR
    op.execute("ALTER TABLE user_patient_mappings ALTER COLUMN user_id TYPE VARCHAR USING user_id::text")
