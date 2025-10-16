"""Add Super Admin Dashboard models

Revision ID: add_super_admin_models
Revises: add_subscription_billing_models
Create Date: 2025-10-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_super_admin_models'
down_revision = 'add_subscription_billing_models'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("""
        CREATE TYPE usagemetrictype AS ENUM (
            'ai_conversations',
            'appointments_booked',
            'patients_added',
            'active_users',
            'storage_used_mb',
            'api_calls',
            'telegram_messages',
            'sms_sent',
            'emails_sent'
        )
    """)
    
    op.execute("""
        CREATE TYPE snapshottype AS ENUM (
            'daily_revenue',
            'weekly_cohort',
            'monthly_churn',
            'usage_summary',
            'cost_summary',
            'health_scores'
        )
    """)
    
    op.execute("""
        CREATE TYPE adminactiontype AS ENUM (
            'create_organization',
            'update_organization',
            'suspend_organization',
            'delete_organization',
            'extend_trial',
            'change_plan',
            'impersonate_user',
            'reset_password',
            'change_user_role',
            'update_subscription',
            'cancel_subscription',
            'refund_payment',
            'view_sensitive_data'
        )
    """)
    
    # Create usage_metrics table
    op.create_table(
        'usage_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('metric_type', postgresql.ENUM(name='usagemetrictype', create_type=False), nullable=False),
        sa.Column('value', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('metric_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usage_metrics_id'), 'usage_metrics', ['id'], unique=False)
    op.create_index('ix_usage_metrics_org_date', 'usage_metrics', ['organization_id', 'date'], unique=False)
    op.create_index('ix_usage_metrics_type_date', 'usage_metrics', ['metric_type', 'date'], unique=False)
    op.create_index('ix_usage_metrics_org_type_date', 'usage_metrics', ['organization_id', 'metric_type', 'date'], unique=False)
    
    # Create cost_tracking table
    op.create_table(
        'cost_tracking',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=True),
        sa.Column('service_name', sa.String(length=100), nullable=False),
        sa.Column('cost_amount', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.00'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('billing_period_start', sa.Date(), nullable=False),
        sa.Column('billing_period_end', sa.Date(), nullable=False),
        sa.Column('usage_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cost_tracking_id'), 'cost_tracking', ['id'], unique=False)
    op.create_index('ix_cost_tracking_org_period', 'cost_tracking', ['organization_id', 'billing_period_start'], unique=False)
    op.create_index('ix_cost_tracking_service_period', 'cost_tracking', ['service_name', 'billing_period_start'], unique=False)
    op.create_index('ix_cost_tracking_period', 'cost_tracking', ['billing_period_start', 'billing_period_end'], unique=False)
    
    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('snapshot_type', postgresql.ENUM(name='snapshottype', create_type=False), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_snapshots_id'), 'analytics_snapshots', ['id'], unique=False)
    op.create_index('ix_analytics_snapshots_type_date', 'analytics_snapshots', ['snapshot_type', 'snapshot_date'], unique=False)
    op.create_index('ix_analytics_snapshots_date', 'analytics_snapshots', ['snapshot_date'], unique=False)
    
    # Create admin_actions table
    op.create_table(
        'admin_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=True),
        sa.Column('action_type', postgresql.ENUM(name='adminactiontype', create_type=False), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('action_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='{}'),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['admin_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_actions_id'), 'admin_actions', ['id'], unique=False)
    op.create_index('ix_admin_actions_admin_user', 'admin_actions', ['admin_user_id'], unique=False)
    op.create_index('ix_admin_actions_target', 'admin_actions', ['target_type', 'target_id'], unique=False)
    op.create_index('ix_admin_actions_type', 'admin_actions', ['action_type'], unique=False)
    op.create_index('ix_admin_actions_created_at', 'admin_actions', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index('ix_admin_actions_created_at', table_name='admin_actions')
    op.drop_index('ix_admin_actions_type', table_name='admin_actions')
    op.drop_index('ix_admin_actions_target', table_name='admin_actions')
    op.drop_index('ix_admin_actions_admin_user', table_name='admin_actions')
    op.drop_index(op.f('ix_admin_actions_id'), table_name='admin_actions')
    op.drop_table('admin_actions')
    
    op.drop_index('ix_analytics_snapshots_date', table_name='analytics_snapshots')
    op.drop_index('ix_analytics_snapshots_type_date', table_name='analytics_snapshots')
    op.drop_index(op.f('ix_analytics_snapshots_id'), table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
    
    op.drop_index('ix_cost_tracking_period', table_name='cost_tracking')
    op.drop_index('ix_cost_tracking_service_period', table_name='cost_tracking')
    op.drop_index('ix_cost_tracking_org_period', table_name='cost_tracking')
    op.drop_index(op.f('ix_cost_tracking_id'), table_name='cost_tracking')
    op.drop_table('cost_tracking')
    
    op.drop_index('ix_usage_metrics_org_type_date', table_name='usage_metrics')
    op.drop_index('ix_usage_metrics_type_date', table_name='usage_metrics')
    op.drop_index('ix_usage_metrics_org_date', table_name='usage_metrics')
    op.drop_index(op.f('ix_usage_metrics_id'), table_name='usage_metrics')
    op.drop_table('usage_metrics')
    
    # Drop enum types
    op.execute('DROP TYPE adminactiontype')
    op.execute('DROP TYPE snapshottype')
    op.execute('DROP TYPE usagemetrictype')

