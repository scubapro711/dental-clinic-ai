"""
BigQuery Billing Service

Queries GCP billing export data from BigQuery.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from decimal import Decimal
from google.cloud import bigquery
from google.oauth2 import service_account
import logging

logger = logging.getLogger(__name__)


class BigQueryBillingService:
    """
    Service for querying GCP billing data from BigQuery.
    
    Prerequisites:
    - Billing export must be enabled in GCP Console
    - BigQuery dataset must be created
    - Service account must have BigQuery Data Viewer role
    """
    
    def __init__(self):
        """Initialize BigQuery client."""
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.dataset_id = os.getenv("GCP_BILLING_DATASET", "billing_export")
        self.table_id = os.getenv("GCP_BILLING_TABLE")  # e.g., gcp_billing_export_v1_XXXXXX_XXXXXX_XXXXXX
        
        # Initialize client with service account credentials if provided
        credentials_path = os.getenv("GCP_BILLING_CREDENTIALS_PATH")
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self.client = bigquery.Client(
                project=self.project_id,
                credentials=credentials
            )
        else:
            # Use default credentials (works in GCP environment)
            self.client = bigquery.Client(project=self.project_id)
        
        self.table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}" if self.table_id else None
    
    def is_configured(self) -> bool:
        """Check if billing export is properly configured."""
        return self.table_ref is not None
    
    def get_total_cost(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """
        Get total cost for a date range.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
        
        Returns:
            Total cost as Decimal
        """
        if not self.is_configured():
            logger.warning("Billing export not configured")
            return Decimal("0.0")
        
        try:
            query = f"""
                SELECT
                    SUM(cost) as total_cost
                FROM `{self.table_ref}`
                WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                    AND cost > 0
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                    bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return Decimal(str(row.total_cost or 0.0))
            
            return Decimal("0.0")
            
        except Exception as e:
            logger.error(f"Error querying total cost: {e}")
            return Decimal("0.0")
    
    def get_cost_by_service(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get cost breakdown by GCP service.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
            limit: Maximum number of services to return
        
        Returns:
            List of dicts with service name, cost, and percentage
        """
        if not self.is_configured():
            logger.warning("Billing export not configured")
            return []
        
        try:
            query = f"""
                WITH total AS (
                    SELECT SUM(cost) as total_cost
                    FROM `{self.table_ref}`
                    WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                        AND cost > 0
                )
                SELECT
                    service.description as service_name,
                    SUM(cost) as total_cost,
                    ROUND((SUM(cost) / (SELECT total_cost FROM total)) * 100, 2) as percentage
                FROM `{self.table_ref}`
                WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                    AND cost > 0
                GROUP BY service_name
                ORDER BY total_cost DESC
                LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                    bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                {
                    "service": row.service_name,
                    "cost": float(row.total_cost),
                    "percentage": float(row.percentage)
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error querying cost by service: {e}")
            return []
    
    def get_cost_by_project(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get cost breakdown by GCP project.
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
            limit: Maximum number of projects to return
        
        Returns:
            List of dicts with project name, cost, and percentage
        """
        if not self.is_configured():
            logger.warning("Billing export not configured")
            return []
        
        try:
            query = f"""
                WITH total AS (
                    SELECT SUM(cost) as total_cost
                    FROM `{self.table_ref}`
                    WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                        AND cost > 0
                )
                SELECT
                    project.name as project_name,
                    SUM(cost) as total_cost,
                    ROUND((SUM(cost) / (SELECT total_cost FROM total)) * 100, 2) as percentage
                FROM `{self.table_ref}`
                WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                    AND cost > 0
                GROUP BY project_name
                ORDER BY total_cost DESC
                LIMIT @limit
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                    bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
                    bigquery.ScalarQueryParameter("limit", "INT64", limit),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                {
                    "project": row.project_name,
                    "cost": float(row.total_cost),
                    "percentage": float(row.percentage)
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error querying cost by project: {e}")
            return []
    
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
        if not self.is_configured():
            logger.warning("Billing export not configured")
            return []
        
        try:
            query = f"""
                SELECT
                    DATE(_PARTITIONTIME) as date,
                    SUM(cost) as total_cost
                FROM `{self.table_ref}`
                WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                    AND cost > 0
                GROUP BY date
                ORDER BY date
            """
            
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                    bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                {
                    "date": row.date.isoformat(),
                    "cost": float(row.total_cost)
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error querying daily costs: {e}")
            return []
    
    def get_cost_by_sku(
        self,
        start_date: datetime,
        end_date: datetime,
        service_name: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get cost breakdown by SKU (Stock Keeping Unit - specific GCP resource).
        
        Args:
            start_date: Start date for cost query
            end_date: End date for cost query
            service_name: Optional filter by service name
            limit: Maximum number of SKUs to return
        
        Returns:
            List of dicts with SKU description, service, and cost
        """
        if not self.is_configured():
            logger.warning("Billing export not configured")
            return []
        
        try:
            service_filter = ""
            if service_name:
                service_filter = "AND service.description = @service_name"
            
            query = f"""
                SELECT
                    sku.description as sku_description,
                    service.description as service_name,
                    SUM(cost) as total_cost
                FROM `{self.table_ref}`
                WHERE DATE(_PARTITIONTIME) BETWEEN @start_date AND @end_date
                    AND cost > 0
                    {service_filter}
                GROUP BY sku_description, service_name
                ORDER BY total_cost DESC
                LIMIT @limit
            """
            
            query_params = [
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
                bigquery.ScalarQueryParameter("limit", "INT64", limit),
            ]
            
            if service_name:
                query_params.append(
                    bigquery.ScalarQueryParameter("service_name", "STRING", service_name)
                )
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            
            return [
                {
                    "sku": row.sku_description,
                    "service": row.service_name,
                    "cost": float(row.total_cost)
                }
                for row in results
            ]
            
        except Exception as e:
            logger.error(f"Error querying cost by SKU: {e}")
            return []


# Singleton instance
_bigquery_billing_service = None


def get_bigquery_billing_service() -> BigQueryBillingService:
    """Get or create BigQuery Billing service instance."""
    global _bigquery_billing_service
    if _bigquery_billing_service is None:
        _bigquery_billing_service = BigQueryBillingService()
    return _bigquery_billing_service

