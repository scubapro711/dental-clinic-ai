"""
Cost Sync Service

Syncs GCP billing data to the CostTracking model.
Runs daily to update cost data.
"""

import logging
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Dict
from sqlalchemy.orm import Session

from app.models.cost_tracking import CostTracking
from app.services.bigquery_billing_service import get_bigquery_billing_service
from app.core.database import get_db

logger = logging.getLogger(__name__)


class CostSyncService:
    """
    Service for syncing GCP billing data to database.
    
    Features:
    - Sync daily costs from BigQuery
    - Store cost breakdown by service
    - Calculate unit economics
    - Track cost trends
    """
    
    def __init__(self, db: Session):
        """Initialize cost sync service."""
        self.db = db
        self.bigquery_service = get_bigquery_billing_service()
    
    def sync_daily_costs(self, target_date: date = None) -> Dict:
        """
        Sync costs for a specific date.
        
        Args:
            target_date: Date to sync costs for (defaults to yesterday)
        
        Returns:
            Dict with sync results
        """
        if target_date is None:
            target_date = date.today() - timedelta(days=1)
        
        logger.info(f"Syncing costs for {target_date}")
        
        if not self.bigquery_service.is_configured():
            logger.warning("BigQuery billing not configured, skipping sync")
            return {
                "status": "skipped",
                "reason": "BigQuery billing export not configured",
                "date": target_date.isoformat()
            }
        
        try:
            # Get cost breakdown by service for the date
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            services = self.bigquery_service.get_cost_by_service(
                start_datetime,
                end_datetime,
                limit=100
            )
            
            # Get total cost
            total_cost = self.bigquery_service.get_total_cost(
                start_datetime,
                end_datetime
            )
            
            # Store or update each service cost
            synced_count = 0
            for service_data in services:
                cost_record = self.db.query(CostTracking).filter(
                    CostTracking.date == target_date,
                    CostTracking.service_name == service_data["service"]
                ).first()
                
                if cost_record:
                    # Update existing record
                    cost_record.cost_amount = Decimal(str(service_data["cost"]))
                    cost_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    cost_record = CostTracking(
                        date=target_date,
                        service_name=service_data["service"],
                        cost_amount=Decimal(str(service_data["cost"])),
                        currency="USD",
                        metadata_json={
                            "percentage": service_data.get("percentage", 0)
                        }
                    )
                    self.db.add(cost_record)
                
                synced_count += 1
            
            self.db.commit()
            
            logger.info(f"Synced {synced_count} service costs for {target_date}")
            
            return {
                "status": "success",
                "date": target_date.isoformat(),
                "total_cost": float(total_cost),
                "services_synced": synced_count
            }
            
        except Exception as e:
            logger.error(f"Error syncing costs: {e}")
            self.db.rollback()
            return {
                "status": "error",
                "date": target_date.isoformat(),
                "error": str(e)
            }
    
    def sync_date_range(
        self,
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Sync costs for a date range.
        
        Args:
            start_date: Start date
            end_date: End date
        
        Returns:
            Dict with sync results
        """
        logger.info(f"Syncing costs from {start_date} to {end_date}")
        
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            result = self.sync_daily_costs(current_date)
            results.append(result)
            current_date += timedelta(days=1)
        
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "error")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        
        return {
            "status": "completed",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_days": len(results),
            "successful": successful,
            "failed": failed,
            "skipped": skipped,
            "results": results
        }
    
    def sync_last_n_days(self, days: int = 7) -> Dict:
        """
        Sync costs for the last N days.
        
        Args:
            days: Number of days to sync
        
        Returns:
            Dict with sync results
        """
        end_date = date.today() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days - 1)
        
        return self.sync_date_range(start_date, end_date)


def sync_yesterday_costs(db: Session) -> Dict:
    """
    Convenience function to sync yesterday's costs.
    Can be called from a cron job or scheduled task.
    
    Args:
        db: Database session
    
    Returns:
        Dict with sync results
    """
    service = CostSyncService(db)
    return service.sync_daily_costs()


def backfill_costs(db: Session, days: int = 30) -> Dict:
    """
    Backfill costs for the last N days.
    Useful for initial setup or catching up after downtime.
    
    Args:
        db: Database session
        days: Number of days to backfill
    
    Returns:
        Dict with sync results
    """
    service = CostSyncService(db)
    return service.sync_last_n_days(days)

