"""
CSV Export Utility

Utilities for exporting dashboard data to CSV format.
"""

import csv
import io
from typing import List, Dict, Any
from datetime import datetime


def export_to_csv(
    data: List[Dict[str, Any]],
    columns: List[str],
    filename: str = None
) -> str:
    """
    Export data to CSV format.
    
    Args:
        data: List of dictionaries containing the data
        columns: List of column names to include
        filename: Optional filename (defaults to timestamp)
    
    Returns:
        CSV content as string
    """
    if filename is None:
        filename = f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction='ignore')
    
    # Write header
    writer.writeheader()
    
    # Write data rows
    for row in data:
        # Convert any non-string values to strings
        cleaned_row = {
            key: str(value) if value is not None else ""
            for key, value in row.items()
            if key in columns
        }
        writer.writerow(cleaned_row)
    
    return output.getvalue()


def export_organizations_csv(organizations: List[Dict]) -> str:
    """Export organizations data to CSV."""
    columns = [
        "id",
        "name",
        "email",
        "subscription_tier",
        "subscription_status",
        "created_at",
        "trial_end",
        "is_active"
    ]
    
    return export_to_csv(organizations, columns, "organizations.csv")


def export_revenue_csv(revenue_data: List[Dict]) -> str:
    """Export revenue data to CSV."""
    columns = [
        "date",
        "mrr",
        "arr",
        "new_mrr",
        "churned_mrr",
        "expansion_mrr",
        "contraction_mrr"
    ]
    
    return export_to_csv(revenue_data, columns, "revenue.csv")


def export_usage_csv(usage_data: List[Dict]) -> str:
    """Export usage metrics to CSV."""
    columns = [
        "organization_id",
        "organization_name",
        "metric_type",
        "value",
        "date"
    ]
    
    return export_to_csv(usage_data, columns, "usage.csv")


def export_costs_csv(cost_data: List[Dict]) -> str:
    """Export cost data to CSV."""
    columns = [
        "date",
        "service_name",
        "cost_amount",
        "currency"
    ]
    
    return export_to_csv(cost_data, columns, "costs.csv")


def export_subscriptions_csv(subscriptions: List[Dict]) -> str:
    """Export subscriptions data to CSV."""
    columns = [
        "id",
        "organization_name",
        "plan_tier",
        "status",
        "plan_price",
        "current_period_start",
        "current_period_end",
        "trial_end",
        "created_at"
    ]
    
    return export_to_csv(subscriptions, columns, "subscriptions.csv")


def export_payments_csv(payments: List[Dict]) -> str:
    """Export payments data to CSV."""
    columns = [
        "id",
        "organization_name",
        "amount",
        "currency",
        "status",
        "payment_method",
        "created_at",
        "paid_at"
    ]
    
    return export_to_csv(payments, columns, "payments.csv")

