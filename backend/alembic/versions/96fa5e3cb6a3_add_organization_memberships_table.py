"""add_organization_memberships_table

Revision ID: 96fa5e3cb6a3
Revises: 3bbb0cae9464
Create Date: 2025-10-07 20:29:45.764756

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96fa5e3cb6a3'
down_revision: Union[str, Sequence[str], None] = '3bbb0cae9464'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create organization_memberships table
    op.create_table(
        'organization_memberships',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('organization_role', sa.String(50), nullable=False),
        sa.Column('functional_role', sa.String(50), nullable=True),
        sa.Column('odoo_partner_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'organization_id', name='uq_user_org')
    )
    
    # Create indexes for performance
    op.create_index('ix_memberships_user', 'organization_memberships', ['user_id'])
    op.create_index('ix_memberships_org', 'organization_memberships', ['organization_id'])
    op.create_index('ix_memberships_odoo', 'organization_memberships', ['odoo_partner_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_memberships_odoo', table_name='organization_memberships')
    op.drop_index('ix_memberships_org', table_name='organization_memberships')
    op.drop_index('ix_memberships_user', table_name='organization_memberships')
    
    # Drop table
    op.drop_table('organization_memberships')
