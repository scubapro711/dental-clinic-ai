"""add telegram messages table

Revision ID: telegram_messages_001
Revises: e47ec69deedc
Create Date: 2025-10-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'telegram_messages_001'
down_revision: Union[str, Sequence[str], None] = 'e47ec69deedc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add telegram_messages table."""
    op.create_table(
        'telegram_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_message_id', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('message_type', sa.String(length=50), nullable=True),
        sa.Column('direction', sa.Enum('INCOMING', 'OUTGOING', name='messagedirection'), nullable=False),
        sa.Column('from_clinic', sa.Boolean(), nullable=True),
        sa.Column('sender_telegram_id', sa.Integer(), nullable=True),
        sa.Column('sender_name', sa.String(length=255), nullable=True),
        sa.Column('is_sent', sa.Boolean(), nullable=True),
        sa.Column('is_delivered', sa.Boolean(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['telegram_conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_telegram_messages_conversation_id'), 'telegram_messages', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_telegram_messages_created_at'), 'telegram_messages', ['created_at'], unique=False)
    op.create_index(op.f('ix_telegram_messages_direction'), 'telegram_messages', ['direction'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop telegram_messages table."""
    op.drop_index(op.f('ix_telegram_messages_direction'), table_name='telegram_messages')
    op.drop_index(op.f('ix_telegram_messages_created_at'), table_name='telegram_messages')
    op.drop_index(op.f('ix_telegram_messages_conversation_id'), table_name='telegram_messages')
    op.drop_table('telegram_messages')
    op.execute('DROP TYPE messagedirection')

