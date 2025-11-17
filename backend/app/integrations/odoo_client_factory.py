# app/integrations/odoo_client_factory.py

import os
import threading
from typing import Optional, Dict

from app.integrations.odoo_client import OdooClient
from app.models.organization import Organization
from app.core.database import SessionLocal

class OdooClientFactory:
    """
    Factory and connection pool for creating organization-aware OdooClient instances.
    
    - Manages a pool of clients to avoid re-creating connections.
    - Provides a default client for backward compatibility.
    - Enforces multi-tenancy with a feature flag.
    """
    _pool: Dict[str, OdooClient] = {}
    _default_client: Optional[OdooClient] = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls, organization_id: Optional[str] = None) -> OdooClient:
        """
        Get an OdooClient instance for a specific organization.

        Args:
            organization_id: The ID of the organization.

        Returns:
            An OdooClient instance.
        """
        # Feature flag for enforcement
        enforce_multi_tenancy = os.getenv("ENFORCE_MULTI_TENANCY", "false").lower() == "true"

        if enforce_multi_tenancy and organization_id is None:
            raise ValueError("organization_id is required when ENFORCE_MULTI_TENANCY is enabled")

        # Backward compatibility: if no org_id, use default client
        if organization_id is None:
            with cls._lock:
                if cls._default_client is None:
                    # Uses environment variables
                    cls._default_client = OdooClient()
                return cls._default_client

        # Multi-tenancy: get org-specific client from pool
        with cls._lock:
            if organization_id not in cls._pool:
                # Query organization from database
                db = SessionLocal()
                try:
                    org = db.query(Organization).filter(Organization.id == organization_id).first()
                    if not org:
                        raise ValueError(f"Organization {organization_id} not found")
                    
                    # If organization has Odoo credentials, use them
                    # Otherwise, fall back to default client
                    if org.odoo_db_name and org.odoo_api_key:
                        # Create a new client with organization-specific credentials
                        cls._pool[organization_id] = OdooClient(
                            url=os.getenv("ODOO_URL"),
                            db=org.odoo_db_name,
                            username=os.getenv("ODOO_USERNAME"),  # Use global username
                            password=org.odoo_api_key  # Use org-specific API key
                        )
                    else:
                        # Fall back to default client if org doesn't have Odoo config
                        if cls._default_client is None:
                            cls._default_client = OdooClient()
                        cls._pool[organization_id] = cls._default_client
                finally:
                    db.close()
            return cls._pool[organization_id]

    @classmethod
    def clear_pool(cls):
        """Clear the connection pool (for testing)."""
        with cls._lock:
            cls._pool.clear()
            cls._default_client = None
