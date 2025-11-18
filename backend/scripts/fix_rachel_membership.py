#!/usr/bin/env python3
"""Fix rachel@dentaflow.ai user membership"""

from sqlalchemy import create_engine, text
from app.core.config import settings
import uuid
from datetime import datetime

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Check if rachel exists
    result = conn.execute(text("SELECT id, email FROM users WHERE email = 'rachel@dentaflow.ai'"))
    rachel = result.fetchone()
    
    if rachel:
        print(f'✅ Rachel exists: {rachel.id}')
        rachel_id = str(rachel.id)
    else:
        print('❌ Rachel does NOT exist. Creating user...')
        # Create rachel user
        rachel_id = str(uuid.uuid4())
        conn.execute(text('''
            INSERT INTO users (id, email, full_name, role, is_active, created_at, updated_at)
            VALUES (:id, :email, :full_name, :role, true, :now, :now)
        '''), {
            'id': rachel_id,
            'email': 'rachel@dentaflow.ai',
            'full_name': 'Dr. Rachel Cohen',
            'role': 'org_admin',
            'now': datetime.utcnow()
        })
        conn.commit()
        print(f'✅ Created Rachel: {rachel_id}')
    
    # Get DentaFlow Clinic org
    result = conn.execute(text("SELECT id FROM organizations WHERE name = 'DentaFlow Clinic'"))
    org = result.fetchone()
    org_id = str(org.id)
    
    print(f'✅ DentaFlow Clinic org: {org_id}')
    
    # Check if membership already exists
    result = conn.execute(text('''
        SELECT id FROM organization_memberships 
        WHERE user_id = :user_id AND organization_id = :org_id
    '''), {'user_id': rachel_id, 'org_id': org_id})
    existing = result.fetchone()
    
    if existing:
        print(f'✅ Membership already exists: {existing.id}')
    else:
        # Create membership
        membership_id = str(uuid.uuid4())
        conn.execute(text('''
            INSERT INTO organization_memberships (
                id, user_id, organization_id, organization_role, functional_role,
                is_active, joined_at, created_at, updated_at
            ) VALUES (
                :id, :user_id, :org_id, :org_role, :func_role,
                true, :now, :now, :now
            )
        '''), {
            'id': membership_id,
            'user_id': rachel_id,
            'org_id': org_id,
            'org_role': 'admin',
            'func_role': 'dentist',
            'now': datetime.utcnow()
        })
        conn.commit()
        
        print(f'✅ Created membership: {membership_id}')
    
    print(f'✅ Rachel is now admin of DentaFlow Clinic!')
    
    # Now update demo checkpoints to use this org_id
    print(f'\n✅ Updating demo checkpoints to use org_id: {org_id}')
    result = conn.execute(text('''
        UPDATE checkpoints
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'::jsonb),
            '{org_id}',
            ('"' || :org_id || '"')::jsonb
        )
        WHERE thread_id LIKE 'demo_%'
    '''), {'org_id': org_id})
    conn.commit()
    print(f'✅ Updated {result.rowcount} checkpoints')
