"""add telegram integration tables

Revision ID: e47ec69deedc
Revises: 8331bae54d16
Create Date: 2025-10-10 08:05:46.036989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e47ec69deedc'
down_revision: Union[str, Sequence[str], None] = '8331bae54d16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add telegram integration tables."""
    
    # Create telegram_users table
    op.create_table(
        'telegram_users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_username', sa.String(length=255), nullable=True),
        sa.Column('telegram_first_name', sa.String(length=255), nullable=True),
        sa.Column('telegram_last_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('patient_id', sa.BigInteger(), nullable=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_active_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_user_id', 'organization_id', name='uq_telegram_user_org')
    )
    op.create_index(op.f('ix_telegram_users_telegram_user_id'), 'telegram_users', ['telegram_user_id'], unique=False)
    op.create_index(op.f('ix_telegram_users_patient_id'), 'telegram_users', ['patient_id'], unique=False)
    
    # Create telegram_conversations table
    op.create_table(
        'telegram_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_flow', sa.String(length=100), nullable=True),
        sa.Column('flow_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['telegram_user_id'], ['telegram_users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telegram_conversations_telegram_user_id'), 'telegram_conversations', ['telegram_user_id'], unique=False)
    op.create_index(op.f('ix_telegram_conversations_conversation_id'), 'telegram_conversations', ['conversation_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop telegram integration tables."""
    op.drop_index(op.f('ix_telegram_conversations_conversation_id'), table_name='telegram_conversations')
    op.drop_index(op.f('ix_telegram_conversations_telegram_user_id'), table_name='telegram_conversations')
    op.drop_table('telegram_conversations')
    
    op.drop_index(op.f('ix_telegram_users_patient_id'), table_name='telegram_users')
    op.drop_index(op.f('ix_telegram_users_telegram_user_id'), table_name='telegram_users')
    op.drop_table('telegram_users')
