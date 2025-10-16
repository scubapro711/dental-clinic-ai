"""Add subscription, payment, and invoice models for SaaS billing

Revision ID: f7a8b9c0d1e2
Revises: ec4c34014113
Create Date: 2025-10-16 05:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f7a8b9c0d1e2'
down_revision = 'ec4c34014113'
branch_labels = None
depends_on = None


def upgrade():
    # Create plan_configurations table
    op.create_table(
        'plan_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plan_key', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('billing_interval', sa.String(length=20), nullable=False),
        sa.Column('trial_days', sa.Integer(), nullable=False),
        sa.Column('max_users', sa.Integer(), nullable=True),
        sa.Column('max_patients', sa.Integer(), nullable=True),
        sa.Column('features', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('stripe_product_id', sa.String(length=255), nullable=True),
        sa.Column('stripe_price_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plan_key'),
        sa.UniqueConstraint('stripe_product_id'),
        sa.UniqueConstraint('stripe_price_id')
    )
    op.create_index(op.f('ix_plan_configurations_plan_key'), 'plan_configurations', ['plan_key'], unique=True)
    
    # Create subscriptionstatus enum
    subscription_status_enum = postgresql.ENUM(
        'trialing', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired',
        name='subscriptionstatus',
        create_type=False
    )
    subscription_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create plantier enum
    plan_tier_enum = postgresql.ENUM(
        'starter', 'professional', 'enterprise',
        name='plantier',
        create_type=False
    )
    plan_tier_enum.create(op.get_bind(), checkfirst=True)
    
    # Create paymentstatus enum
    payment_status_enum = postgresql.ENUM(
        'succeeded', 'pending', 'failed', 'canceled', 'requires_action',
        name='paymentstatus',
        create_type=False
    )
    payment_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create invoicestatus enum
    invoice_status_enum = postgresql.ENUM(
        'draft', 'open', 'paid', 'void', 'uncollectible',
        name='invoicestatus',
        create_type=False
    )
    invoice_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_customer_id', sa.String(length=255), nullable=False),
        sa.Column('plan_tier', sa.Enum('starter', 'professional', 'enterprise', name='plantier'), nullable=False),
        sa.Column('status', sa.Enum('trialing', 'active', 'past_due', 'canceled', 'unpaid', 'incomplete', 'incomplete_expired', name='subscriptionstatus'), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trial_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancel_at_period_end', sa.Boolean(), nullable=False),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id'),
        sa.UniqueConstraint('stripe_subscription_id')
    )
    op.create_index(op.f('ix_subscriptions_organization_id'), 'subscriptions', ['organization_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_stripe_subscription_id'), 'subscriptions', ['stripe_subscription_id'], unique=True)
    op.create_index(op.f('ix_subscriptions_stripe_customer_id'), 'subscriptions', ['stripe_customer_id'], unique=False)
    
    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=255), nullable=False),
        sa.Column('stripe_charge_id', sa.String(length=255), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.Enum('succeeded', 'pending', 'failed', 'canceled', 'requires_action', name='paymentstatus'), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_method_details', sa.Text(), nullable=True),
        sa.Column('failure_code', sa.String(length=100), nullable=True),
        sa.Column('failure_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('succeeded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_payment_intent_id'),
        sa.UniqueConstraint('stripe_charge_id')
    )
    op.create_index(op.f('ix_payments_subscription_id'), 'payments', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_payments_stripe_payment_intent_id'), 'payments', ['stripe_payment_intent_id'], unique=True)
    op.create_index(op.f('ix_payments_stripe_charge_id'), 'payments', ['stripe_charge_id'], unique=True)
    
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stripe_invoice_id', sa.String(length=255), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('amount_due', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('amount_paid', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('amount_remaining', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.Enum('draft', 'open', 'paid', 'void', 'uncollectible', name='invoicestatus'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('invoice_pdf', sa.String(length=500), nullable=True),
        sa.Column('hosted_invoice_url', sa.String(length=500), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stripe_invoice_id'),
        sa.UniqueConstraint('invoice_number')
    )
    op.create_index(op.f('ix_invoices_subscription_id'), 'invoices', ['subscription_id'], unique=False)
    op.create_index(op.f('ix_invoices_stripe_invoice_id'), 'invoices', ['stripe_invoice_id'], unique=True)


def downgrade():
    # Drop tables
    op.drop_index(op.f('ix_invoices_stripe_invoice_id'), table_name='invoices')
    op.drop_index(op.f('ix_invoices_subscription_id'), table_name='invoices')
    op.drop_table('invoices')
    
    op.drop_index(op.f('ix_payments_stripe_charge_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_stripe_payment_intent_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_subscription_id'), table_name='payments')
    op.drop_table('payments')
    
    op.drop_index(op.f('ix_subscriptions_stripe_customer_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_stripe_subscription_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_organization_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    
    op.drop_index(op.f('ix_plan_configurations_plan_key'), table_name='plan_configurations')
    op.drop_table('plan_configurations')
    
    # Drop enums
    sa.Enum(name='invoicestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymentstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='plantier').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionstatus').drop(op.get_bind(), checkfirst=True)

