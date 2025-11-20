"""add demo_leads table

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2025-11-20 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    # Create demo_leads table
    op.create_table(
        'demo_leads',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False, comment="Lead's full name"),
        sa.Column('email', sa.String(), nullable=False, comment="Lead's email address"),
        sa.Column('phone', sa.String(), nullable=False, comment="Lead's phone number"),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment="When demo session was created"),
        sa.Column('converted', sa.Boolean(), nullable=True, comment="Did they sign up?"),
        sa.Column('converted_at', sa.DateTime(), nullable=True, comment="When they signed up"),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on email for faster lookups
    op.create_index(op.f('ix_demo_leads_email'), 'demo_leads', ['email'], unique=False)
    op.create_index(op.f('ix_demo_leads_created_at'), 'demo_leads', ['created_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_demo_leads_created_at'), table_name='demo_leads')
    op.drop_index(op.f('ix_demo_leads_email'), table_name='demo_leads')
    
    # Drop table
    op.drop_table('demo_leads')
