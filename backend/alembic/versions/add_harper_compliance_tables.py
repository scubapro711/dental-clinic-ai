"""Add Harper compliance tables

Revision ID: harper_compliance_001
Revises: 
Create Date: 2025-01-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'harper_compliance_001'
down_revision = '5a8c2b9d3e4f'  # add_mfa_columns_to_users
branch_labels = None
depends_on = None


def upgrade():
    # Create compliance_alerts table
    op.create_table(
        'compliance_alerts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('alert_type', sa.Enum(
            'BAA_EXPIRING', 'BAA_EXPIRED', 'PHI_COMPLIANCE_ISSUE', 
            'SECURITY_GAP', 'ACCESS_ANOMALY', 'RISK_THRESHOLD_EXCEEDED',
            'BREACH_DETECTED', 'PATIENT_RIGHTS_VIOLATION', 'AUDIT_FINDING',
            'COMPLIANCE_SCORE_DROP',
            name='alerttype'
        ), nullable=False),
        sa.Column('severity', sa.Enum(
            'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO',
            name='alertseverity'
        ), nullable=False),
        sa.Column('status', sa.Enum(
            'OPEN', 'ACKNOWLEDGED', 'IN_PROGRESS', 'RESOLVED', 'DISMISSED',
            name='alertstatus'
        ), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('action_required', sa.Text(), nullable=True),
        sa.Column('deadline', sa.String(length=100), nullable=True),
        sa.Column('deadline_date', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('acknowledged_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(), nullable=True),
        sa.Column('dismissed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('dismissal_reason', sa.Text(), nullable=True),
        sa.Column('related_entity_type', sa.String(length=50), nullable=True),
        sa.Column('related_entity_id', sa.Integer(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True),
        sa.Column('notification_sent_at', sa.DateTime(), nullable=True),
        sa.Column('notification_channels', sa.JSON(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('recurrence_key', sa.String(length=255), nullable=True),
        sa.Column('last_occurrence_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['dismissed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for compliance_alerts
    op.create_index('idx_org_status', 'compliance_alerts', ['organization_id', 'status'])
    op.create_index('idx_org_severity', 'compliance_alerts', ['organization_id', 'severity'])
    op.create_index('idx_org_type', 'compliance_alerts', ['organization_id', 'alert_type'])
    op.create_index('idx_org_created', 'compliance_alerts', ['organization_id', 'created_at'])
    op.create_index('idx_deadline', 'compliance_alerts', ['deadline_date'])
    op.create_index('idx_recurrence', 'compliance_alerts', ['recurrence_key', 'created_at'])
    op.create_index(op.f('ix_compliance_alerts_organization_id'), 'compliance_alerts', ['organization_id'])
    op.create_index(op.f('ix_compliance_alerts_alert_type'), 'compliance_alerts', ['alert_type'])
    op.create_index(op.f('ix_compliance_alerts_severity'), 'compliance_alerts', ['severity'])
    op.create_index(op.f('ix_compliance_alerts_status'), 'compliance_alerts', ['status'])
    op.create_index(op.f('ix_compliance_alerts_created_at'), 'compliance_alerts', ['created_at'])
    op.create_index(op.f('ix_compliance_alerts_recurrence_key'), 'compliance_alerts', ['recurrence_key'])

    # Create compliance_metrics table
    op.create_table(
        'compliance_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('period_type', sa.String(length=20), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=True),
        sa.Column('period_end', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for compliance_metrics
    op.create_index('idx_org_metric_time', 'compliance_metrics', ['organization_id', 'metric_type', 'recorded_at'])
    op.create_index('idx_period', 'compliance_metrics', ['period_type', 'period_start'])
    op.create_index(op.f('ix_compliance_metrics_organization_id'), 'compliance_metrics', ['organization_id'])
    op.create_index(op.f('ix_compliance_metrics_recorded_at'), 'compliance_metrics', ['recorded_at'])
    op.create_index(op.f('ix_compliance_metrics_metric_type'), 'compliance_metrics', ['metric_type'])


def downgrade():
    # Drop compliance_metrics table
    op.drop_index(op.f('ix_compliance_metrics_metric_type'), table_name='compliance_metrics')
    op.drop_index(op.f('ix_compliance_metrics_recorded_at'), table_name='compliance_metrics')
    op.drop_index(op.f('ix_compliance_metrics_organization_id'), table_name='compliance_metrics')
    op.drop_index('idx_period', table_name='compliance_metrics')
    op.drop_index('idx_org_metric_time', table_name='compliance_metrics')
    op.drop_table('compliance_metrics')
    
    # Drop compliance_alerts table
    op.drop_index(op.f('ix_compliance_alerts_recurrence_key'), table_name='compliance_alerts')
    op.drop_index(op.f('ix_compliance_alerts_created_at'), table_name='compliance_alerts')
    op.drop_index(op.f('ix_compliance_alerts_status'), table_name='compliance_alerts')
    op.drop_index(op.f('ix_compliance_alerts_severity'), table_name='compliance_alerts')
    op.drop_index(op.f('ix_compliance_alerts_alert_type'), table_name='compliance_alerts')
    op.drop_index(op.f('ix_compliance_alerts_organization_id'), table_name='compliance_alerts')
    op.drop_index('idx_recurrence', table_name='compliance_alerts')
    op.drop_index('idx_deadline', table_name='compliance_alerts')
    op.drop_index('idx_org_created', table_name='compliance_alerts')
    op.drop_index('idx_org_type', table_name='compliance_alerts')
    op.drop_index('idx_org_severity', table_name='compliance_alerts')
    op.drop_index('idx_org_status', table_name='compliance_alerts')
    op.drop_table('compliance_alerts')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS alertseverity')
    op.execute('DROP TYPE IF EXISTS alerttype')

