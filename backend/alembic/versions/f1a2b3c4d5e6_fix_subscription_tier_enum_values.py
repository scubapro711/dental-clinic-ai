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
    
    The original migration created the enum with uppercase values (BASIC, PROFESSIONAL, ENTERPRISE)
    but the Python model uses lowercase values (basic, professional, enterprise).
    This migration fixes the mismatch.
    """
    # Check if any organizations exist
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM organizations"))
    org_count = result.scalar()
    
    if org_count == 0:
        # No data exists - simple fix
        # Drop the old enum type (CASCADE will handle the column)
        op.execute("DROP TYPE IF EXISTS subscriptiontier CASCADE")
        
        # Create new enum with lowercase values
        op.execute("CREATE TYPE subscriptiontier AS ENUM ('basic', 'professional', 'enterprise')")
        
        # Recreate the column with the new enum type
        op.execute("""
            ALTER TABLE organizations 
            ALTER COLUMN subscription_tier TYPE subscriptiontier 
            USING subscription_tier::text::subscriptiontier
        """)
    else:
        # Data exists - safe migration
        # Create new enum type with lowercase values
        op.execute("CREATE TYPE subscriptiontier_new AS ENUM ('basic', 'professional', 'enterprise')")
        
        # Migrate existing data from uppercase to lowercase
        op.execute("""
            ALTER TABLE organizations 
            ALTER COLUMN subscription_tier TYPE subscriptiontier_new 
            USING (
                CASE 
                    WHEN subscription_tier::text = 'BASIC' THEN 'basic'::subscriptiontier_new
                    WHEN subscription_tier::text = 'PROFESSIONAL' THEN 'professional'::subscriptiontier_new
                    WHEN subscription_tier::text = 'ENTERPRISE' THEN 'enterprise'::subscriptiontier_new
                    -- Handle lowercase values if they already exist
                    WHEN subscription_tier::text = 'basic' THEN 'basic'::subscriptiontier_new
                    WHEN subscription_tier::text = 'professional' THEN 'professional'::subscriptiontier_new
                    WHEN subscription_tier::text = 'enterprise' THEN 'enterprise'::subscriptiontier_new
                END
            )
        """)
        
        # Drop old enum type
        op.execute("DROP TYPE subscriptiontier")
        
        # Rename new enum type to original name
        op.execute("ALTER TYPE subscriptiontier_new RENAME TO subscriptiontier")


def downgrade() -> None:
    """Downgrade schema - Revert to uppercase enum values.
    
    This is provided for completeness but should rarely be used.
    """
    # Create old enum type with uppercase values
    op.execute("CREATE TYPE subscriptiontier_old AS ENUM ('BASIC', 'PROFESSIONAL', 'ENTERPRISE')")
    
    # Migrate data back to uppercase
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
    
    # Drop new enum type
    op.execute("DROP TYPE subscriptiontier")
    
    # Rename old enum type back
    op.execute("ALTER TYPE subscriptiontier_old RENAME TO subscriptiontier")
