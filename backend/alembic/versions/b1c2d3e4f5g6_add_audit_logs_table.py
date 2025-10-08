"""add audit_logs table

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2025-10-08 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '''b1c2d3e4f5g6'''
down_revision: Union[str, Sequence[str], None] = '''a1b2c3d4e5f6'''
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        '''audit_logs''',
        sa.Column('''id''', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('''user_id''', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('''user_email''', sa.String(255), nullable=False),
        sa.Column('''user_role''', sa.String(50)),
        sa.Column('''action''', sa.String(50), nullable=False),
        sa.Column('''resource_type''', sa.String(100), nullable=False),
        sa.Column('''resource_id''', sa.String(255)),
        sa.Column('''timestamp''', sa.DateTime(), nullable=False),
        sa.Column('''ip_address''', sa.String(45)),
        sa.Column('''user_agent''', sa.String(500)),
        sa.Column('''reason''', sa.Text()),
        sa.Column('''endpoint''', sa.String(500)),
        sa.Column('''method''', sa.String(10)),
        sa.Column('''changes''', postgresql.JSONB()),
        sa.Column('''metadata''', postgresql.JSONB()),
        sa.Column('''organization_id''', postgresql.UUID(as_uuid=True)),
        sa.Column('''status''', sa.String(20), server_default='''success'''),
        sa.Column('''error_message''', sa.Text())
    )
    
    # Create indexes
    op.create_index('''ix_audit_logs_user_id''', '''audit_logs''', ['''user_id'''])
    op.create_index('''ix_audit_logs_action''', '''audit_logs''', ['''action'''])
    op.create_index('''ix_audit_logs_resource_type''', '''audit_logs''', ['''resource_type'''])
    op.create_index('''ix_audit_logs_resource_id''', '''audit_logs''', ['''resource_id'''])
    op.create_index('''ix_audit_logs_timestamp''', '''audit_logs''', ['''timestamp'''])
    op.create_index('''ix_audit_logs_organization_id''', '''audit_logs''', ['''organization_id'''])
    op.create_index('''ix_audit_logs_user_timestamp''', '''audit_logs''', ['''user_id''', '''timestamp'''])
    op.create_index('''ix_audit_logs_resource''', '''audit_logs''', ['''resource_type''', '''resource_id'''])
    op.create_index('''ix_audit_logs_org_timestamp''', '''audit_logs''', ['''organization_id''', '''timestamp'''])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('''ix_audit_logs_org_timestamp''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_resource''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_user_timestamp''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_organization_id''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_timestamp''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_resource_id''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_resource_type''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_action''', table_name='''audit_logs''')
    op.drop_index('''ix_audit_logs_user_id''', table_name='''audit_logs''')
    op.drop_table('''audit_logs''')
