"""add pilot applications table

Revision ID: add_pilot_apps
Revises: 
Create Date: 2025-10-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_pilot_apps'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pilot_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clinic_name', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=50), nullable=False),
        sa.Column('clinic_size', sa.String(length=50), nullable=False),
        sa.Column('monthly_patients', sa.String(length=50), nullable=False),
        sa.Column('current_software', sa.String(length=255), nullable=True),
        sa.Column('team_size', sa.String(length=50), nullable=False),
        sa.Column('ai_experience', sa.String(length=50), nullable=False),
        sa.Column('primary_goal', sa.String(length=100), nullable=False),
        sa.Column('timeline', sa.String(length=50), nullable=False),
        sa.Column('budget', sa.String(length=50), nullable=True),
        sa.Column('willing_to_provide_feedback', sa.Boolean(), default=False),
        sa.Column('willing_to_be_referenced', sa.Boolean(), default=False),
        sa.Column('agreed_to_terms', sa.Boolean(), nullable=False, default=False),
        sa.Column('status', sa.Enum('PENDING', 'REVIEWING', 'APPROVED', 'REJECTED', 'WAITLIST', name='applicationstatus'), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pilot_applications_email'), 'pilot_applications', ['email'], unique=False)
    op.create_index(op.f('ix_pilot_applications_id'), 'pilot_applications', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_pilot_applications_id'), table_name='pilot_applications')
    op.drop_index(op.f('ix_pilot_applications_email'), table_name='pilot_applications')
    op.drop_table('pilot_applications')
    op.execute('DROP TYPE applicationstatus')
