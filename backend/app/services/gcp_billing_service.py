"""
GCP Billing Service

Integrates with Google Cloud Billing API to fetch real cost data.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal
from google.cloud import billing_v1
from google.cloud.billing_v1 import CloudCatalogClient
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)


class GCPBillingService:
    """
    Service for interacting with GCP Billing API.
    
    Features:
    - Fetch billing data for a specific billing account
    - Get cost breakdown by service
    - Get cost breakdown by project
    - Calculate daily/monthly costs
    - Export cost data for analysis
    """
    
    def __init__(self):
        """Initialize GCP Billing client."""
        self.billing_account_id = os.getenv("GCP_BILLING_ACCOUNT_ID")
        self.project_id = os.getenv("GCP_PROJECT_ID")
        
        # Initialize client with service account credentials if provided
        credentials_path = os.getenv("GCP_BILLING_CREDENTIALS_PATH")
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = billing_v1.CloudBillingClient(credentials=credentials)
            self.catalog_client = CloudCatalogClient(credentials=credentials)
        else:
            # Use default credentials (works in GCP environment)
            self.client = billing_v1.CloudBillingClient()
            self.catalog_client = CloudCatalogClient()
    
    def get_billing_account_costs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Get total costs for the billing account in a date range.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
        
        Returns:
            Dict with total cost and breakdown by service
        """
        try:
            # Note: This is a simplified implementation
            # In production, you would use BigQuery to query billing export data
            # See: https://cloud.google.com/billing/docs/how-to/export-data-bigquery
            
            logger.info(f"Fetching billing data from {start_date} to {end_date}")
            
            # For now, return mock data structure
            # TODO: Implement actual BigQuery query when billing export is set up
            return {
                "total_cost": 0.0,
                "currency": "USD",
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "by_service": [],
                "note": "Billing export to BigQuery not yet configured"
            }
            
        except Exception as e:
            logger.error(f"Error fetching billing data: {e}")
            raise
    
    def get_cost_by_service(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get cost breakdown by GCP service.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
        
        Returns:
            List of dicts with service name and cost
        """
        try:
            # TODO: Implement BigQuery query
            # Example query:
            # SELECT
            #   service.description as service_name,
            #   SUM(cost) as total_cost
            # FROM `project.dataset.gcp_billing_export_v1_BILLING_ACCOUNT_ID`
            # WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
            # GROUP BY service_name
            # ORDER BY total_cost DESC
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching cost by service: {e}")
            raise
    
    def get_cost_by_project(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get cost breakdown by GCP project.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
        
        Returns:
            List of dicts with project name and cost
        """
        try:
            # TODO: Implement BigQuery query
            return []
            
        except Exception as e:
            logger.error(f"Error fetching cost by project: {e}")
            raise
    
    def get_daily_costs(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """
        Get daily cost breakdown.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
        
        Returns:
            List of dicts with date and cost
        """
        try:
            # TODO: Implement BigQuery query
            # Example query:
            # SELECT
            #   DATE(_PARTITIONTIME) as date,
            #   SUM(cost) as total_cost
            # FROM `project.dataset.gcp_billing_export_v1_BILLING_ACCOUNT_ID`
            # WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
            # GROUP BY date
            # ORDER BY date
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching daily costs: {e}")
            raise
    
    def setup_billing_export(self) -> Dict:
        """
        Instructions for setting up billing export to BigQuery.
        
        Returns:
            Dict with setup instructions
        """
        return {
            "status": "not_configured",
            "instructions": [
                "1. Go to GCP Console > Billing > Billing Export",
                "2. Click 'Enable Billing Export'",
                "3. Select or create a BigQuery dataset",
                "4. Choose 'Detailed usage cost' export type",
                "5. Save the configuration",
                "6. Wait 24-48 hours for data to populate",
                "7. Update GCP_BILLING_DATASET environment variable",
                "8. Grant BigQuery Data Viewer role to service account"
            ],
            "documentation": "https://cloud.google.com/billing/docs/how-to/export-data-bigquery"
        }


# Singleton instance
_gcp_billing_service = None


def get_gcp_billing_service() -> GCPBillingService:
    """Get or create GCP Billing service instance."""
    global _gcp_billing_service
    if _gcp_billing_service is None:
        _gcp_billing_service = GCPBillingService()
    return _gcp_billing_service

