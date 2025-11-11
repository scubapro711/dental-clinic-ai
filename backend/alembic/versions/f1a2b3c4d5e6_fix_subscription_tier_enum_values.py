"""fix subscription_tier enum values

Revision ID: f1a2b3c4d5e6
Revises: ec4c34014113
Create Date: 2025-11-06 01:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'ec4c34014113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Fix subscription_tier enum to use lowercase values.
    
    This migration is designed to fix existing databases that have uppercase enum values.
    For new databases, the initial migration already creates the enum correctly.
    """
    conn = op.get_bind()
    
    # Check if organizations table exists
    table_check = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'organizations')"
    ))
    table_exists = table_check.scalar()
    
    if not table_exists:
        # Table doesn't exist yet - skip this migration
        return
    
    # Check if subscription_tier column exists
    column_check = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'subscription_tier'
        )
    """))
    column_exists = column_check.scalar()
    
    if not column_exists:
        # Column doesn't exist yet - skip this migration
        return
    
    # Check what enum values currently exist
    enum_check = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = 'subscriptiontier'
            AND e.enumlabel = 'BASIC'
        )
    """))
    has_uppercase = enum_check.scalar()
    
    if not has_uppercase:
        # Enum already has lowercase values - skip this migration
        return
    
    # At this point, we know:
    # - Table exists
    # - Column exists
    # - Enum has uppercase values that need fixing
    
    # Check if any data exists
    result = conn.execute(sa.text("SELECT COUNT(*) FROM organizations"))
    org_count = result.scalar()
    
    if org_count == 0:
        # No data - safe to drop and recreate
        op.execute("DROP TYPE subscriptiontier CASCADE")
        op.execute("CREATE TYPE subscriptiontier AS ENUM ('basic', 'professional', 'enterprise')")
        op.execute("""
            ALTER TABLE organizations 
            ADD COLUMN subscription_tier subscriptiontier NOT NULL DEFAULT 'basic'
        """)
    else:
        # Data exists - careful migration
        op.execute("CREATE TYPE subscriptiontier_new AS ENUM ('basic', 'professional', 'enterprise')")
        
        op.execute("""
            ALTER TABLE organizations 
            ALTER COLUMN subscription_tier TYPE subscriptiontier_new 
            USING (
                CASE 
                    WHEN subscription_tier::text = 'BASIC' THEN 'basic'::subscriptiontier_new
                    WHEN subscription_tier::text = 'PROFESSIONAL' THEN 'professional'::subscriptiontier_new
                    WHEN subscription_tier::text = 'ENTERPRISE' THEN 'enterprise'::subscriptiontier_new
                    WHEN subscription_tier::text = 'basic' THEN 'basic'::subscriptiontier_new
                    WHEN subscription_tier::text = 'professional' THEN 'professional'::subscriptiontier_new
                    WHEN subscription_tier::text = 'enterprise' THEN 'enterprise'::subscriptiontier_new
                END
            )
        """)
        
        op.execute("DROP TYPE subscriptiontier")
        op.execute("ALTER TYPE subscriptiontier_new RENAME TO subscriptiontier")


def downgrade() -> None:
    """Downgrade schema - Revert to uppercase enum values."""
    conn = op.get_bind()
    
    # Check if we need to do anything
    table_check = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'organizations')"
    ))
    if not table_check.scalar():
        return
    
    column_check = conn.execute(sa.text("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'subscription_tier'
        )
    """))
    if not column_check.scalar():
        return
    
    # Perform downgrade
    op.execute("CREATE TYPE subscriptiontier_old AS ENUM ('BASIC', 'PROFESSIONAL', 'ENTERPRISE')")
    
    op.execute("""
        ALTER TABLE organizations 
        ALTER COLUMN subscription_tier TYPE subscriptiontier_old 
        USING (
            CASE 
                WHEN subscription_tier::text = 'basic' THEN 'BASIC'::subscriptiontier_old
                WHEN subscription_tier::text = 'professional' THEN 'PROFESSIONAL'::subscriptiontier_old
                WHEN subscription_tier::text = 'enterprise' THEN 'ENTERPRISE'::subscriptiontier_old
            END
        )
    """)
    
    op.execute("DROP TYPE subscriptiontier")
    op.execute("ALTER TYPE subscriptiontier_old RENAME TO subscriptiontier")
