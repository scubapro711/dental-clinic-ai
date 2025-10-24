"""
Unit Tests for CSV Export Utility

Tests for app.utils.csv_export module including:
- Basic CSV export functionality
- Column filtering
- Data type handling
- Specialized export functions (organizations, revenue, usage, costs, subscriptions, payments)
- Edge cases (empty data, None values, extra fields)
"""

import pytest
import csv
import io
from datetime import datetime
from unittest.mock import patch

from app.utils.csv_export import (
    export_to_csv,
    export_organizations_csv,
    export_revenue_csv,
    export_usage_csv,
    export_costs_csv,
    export_subscriptions_csv,
    export_payments_csv
)


@pytest.mark.unit
@pytest.mark.utils
class TestExportToCSV:
    """Test basic CSV export functionality."""
    
    def test_export_simple_data(self):
        """Test exporting simple data to CSV."""
        data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "London"}
        ]
        columns = ["name", "age", "city"]
        
        result = export_to_csv(data, columns)
        
        assert result is not None
        assert "name,age,city" in result
        assert "Alice,30,New York" in result
        assert "Bob,25,London" in result
    
    def test_export_with_column_filtering(self):
        """Test that only specified columns are exported."""
        data = [
            {"name": "Alice", "age": 30, "city": "New York", "secret": "hidden"},
            {"name": "Bob", "age": 25, "city": "London", "secret": "hidden"}
        ]
        columns = ["name", "city"]  # Don't include age or secret
        
        result = export_to_csv(data, columns)
        
        assert "name,city" in result
        assert "Alice,New York" in result
        assert "Bob,London" in result
        assert "age" not in result
        assert "secret" not in result
        assert "30" not in result
    
    def test_export_with_none_values(self):
        """Test handling of None values."""
        data = [
            {"name": "Alice", "age": 30, "city": None},
            {"name": "Bob", "age": None, "city": "London"}
        ]
        columns = ["name", "age", "city"]
        
        result = export_to_csv(data, columns)
        
        # None values should be converted to empty strings
        assert result is not None
        lines = result.strip().split('\n')
        assert len(lines) == 3  # header + 2 data rows
    
    def test_export_with_non_string_values(self):
        """Test handling of non-string values."""
        data = [
            {"name": "Alice", "age": 30, "score": 95.5, "active": True},
            {"name": "Bob", "age": 25, "score": 87.3, "active": False}
        ]
        columns = ["name", "age", "score", "active"]
        
        result = export_to_csv(data, columns)
        
        # All values should be converted to strings
        assert "30" in result
        assert "95.5" in result
        assert "True" in result
        assert "False" in result
    
    def test_export_empty_data(self):
        """Test exporting empty data list."""
        data = []
        columns = ["name", "age", "city"]
        
        result = export_to_csv(data, columns)
        
        # Should still have header
        assert "name,age,city" in result
        lines = result.strip().split('\n')
        assert len(lines) == 1  # Only header
    
    def test_export_with_custom_filename(self):
        """Test that custom filename is accepted."""
        data = [{"name": "Alice"}]
        columns = ["name"]
        
        # Should not raise error
        result = export_to_csv(data, columns, filename="custom.csv")
        
        assert result is not None
    
    def test_export_with_missing_columns(self):
        """Test handling of missing columns in data."""
        data = [
            {"name": "Alice", "age": 30},  # Missing city
            {"name": "Bob", "city": "London"}  # Missing age
        ]
        columns = ["name", "age", "city"]
        
        result = export_to_csv(data, columns)
        
        # Should handle missing columns gracefully
        assert result is not None
        lines = result.strip().split('\n')
        assert len(lines) == 3  # header + 2 data rows
    
    def test_export_with_extra_fields(self):
        """Test that extra fields in data are ignored."""
        data = [
            {"name": "Alice", "age": 30, "extra1": "ignore", "extra2": "ignore"}
        ]
        columns = ["name", "age"]
        
        result = export_to_csv(data, columns)
        
        # Extra fields should be ignored
        assert "extra1" not in result
        assert "extra2" not in result
        assert "ignore" not in result
    
    def test_export_csv_format(self):
        """Test that output is valid CSV format."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        columns = ["name", "age"]
        
        result = export_to_csv(data, columns)
        
        # Parse the CSV to verify it's valid
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == "30"
        assert rows[1]["name"] == "Bob"
        assert rows[1]["age"] == "25"


@pytest.mark.unit
@pytest.mark.utils
class TestExportOrganizationsCSV:
    """Test organizations CSV export."""
    
    def test_export_organizations(self):
        """Test exporting organizations data."""
        organizations = [
            {
                "id": "org1",
                "name": "Clinic A",
                "email": "contact@clinica.com",
                "subscription_tier": "professional",
                "subscription_status": "active",
                "created_at": "2024-01-01",
                "trial_end": "2024-02-01",
                "is_active": True
            },
            {
                "id": "org2",
                "name": "Clinic B",
                "email": "contact@clinicb.com",
                "subscription_tier": "enterprise",
                "subscription_status": "active",
                "created_at": "2024-01-15",
                "trial_end": None,
                "is_active": True
            }
        ]
        
        result = export_organizations_csv(organizations)
        
        assert result is not None
        assert "id,name,email,subscription_tier" in result
        assert "Clinic A" in result
        assert "Clinic B" in result
        assert "professional" in result
        assert "enterprise" in result
    
    def test_export_empty_organizations(self):
        """Test exporting empty organizations list."""
        result = export_organizations_csv([])
        
        # Should have header
        assert "id,name,email" in result


@pytest.mark.unit
@pytest.mark.utils
class TestExportRevenueCSV:
    """Test revenue CSV export."""
    
    def test_export_revenue(self):
        """Test exporting revenue data."""
        revenue_data = [
            {
                "date": "2024-01-01",
                "mrr": 10000,
                "arr": 120000,
                "new_mrr": 2000,
                "churned_mrr": 500,
                "expansion_mrr": 1000,
                "contraction_mrr": 200
            },
            {
                "date": "2024-02-01",
                "mrr": 12000,
                "arr": 144000,
                "new_mrr": 3000,
                "churned_mrr": 600,
                "expansion_mrr": 1500,
                "contraction_mrr": 300
            }
        ]
        
        result = export_revenue_csv(revenue_data)
        
        assert result is not None
        assert "date,mrr,arr,new_mrr" in result
        assert "10000" in result
        assert "120000" in result
        assert "12000" in result


@pytest.mark.unit
@pytest.mark.utils
class TestExportUsageCSV:
    """Test usage CSV export."""
    
    def test_export_usage(self):
        """Test exporting usage metrics."""
        usage_data = [
            {
                "organization_id": "org1",
                "organization_name": "Clinic A",
                "metric_type": "api_calls",
                "value": 1500,
                "date": "2024-01-01"
            },
            {
                "organization_id": "org2",
                "organization_name": "Clinic B",
                "metric_type": "storage_gb",
                "value": 25,
                "date": "2024-01-01"
            }
        ]
        
        result = export_usage_csv(usage_data)
        
        assert result is not None
        assert "organization_id,organization_name,metric_type" in result
        assert "Clinic A" in result
        assert "api_calls" in result
        assert "1500" in result


@pytest.mark.unit
@pytest.mark.utils
class TestExportCostsCSV:
    """Test costs CSV export."""
    
    def test_export_costs(self):
        """Test exporting cost data."""
        cost_data = [
            {
                "date": "2024-01-01",
                "service_name": "OpenAI",
                "cost_amount": 500.50,
                "currency": "USD"
            },
            {
                "date": "2024-01-01",
                "service_name": "GCP",
                "cost_amount": 300.25,
                "currency": "USD"
            }
        ]
        
        result = export_costs_csv(cost_data)
        
        assert result is not None
        assert "date,service_name,cost_amount,currency" in result
        assert "OpenAI" in result
        assert "500.5" in result
        assert "USD" in result


@pytest.mark.unit
@pytest.mark.utils
class TestExportSubscriptionsCSV:
    """Test subscriptions CSV export."""
    
    def test_export_subscriptions(self):
        """Test exporting subscriptions data."""
        subscriptions = [
            {
                "id": "sub1",
                "organization_name": "Clinic A",
                "plan_tier": "professional",
                "status": "active",
                "plan_price": 799,
                "current_period_start": "2024-01-01",
                "current_period_end": "2024-02-01",
                "trial_end": None,
                "created_at": "2024-01-01"
            },
            {
                "id": "sub2",
                "organization_name": "Clinic B",
                "plan_tier": "enterprise",
                "status": "trialing",
                "plan_price": 1499,
                "current_period_start": "2024-01-15",
                "current_period_end": "2024-02-15",
                "trial_end": "2024-02-15",
                "created_at": "2024-01-15"
            }
        ]
        
        result = export_subscriptions_csv(subscriptions)
        
        assert result is not None
        assert "id,organization_name,plan_tier,status" in result
        assert "Clinic A" in result
        assert "professional" in result
        assert "799" in result
        assert "trialing" in result


@pytest.mark.unit
@pytest.mark.utils
class TestExportPaymentsCSV:
    """Test payments CSV export."""
    
    def test_export_payments(self):
        """Test exporting payments data."""
        payments = [
            {
                "id": "pay1",
                "organization_name": "Clinic A",
                "amount": 799,
                "currency": "USD",
                "status": "succeeded",
                "payment_method": "card",
                "created_at": "2024-01-01",
                "paid_at": "2024-01-01"
            },
            {
                "id": "pay2",
                "organization_name": "Clinic B",
                "amount": 1499,
                "currency": "USD",
                "status": "pending",
                "payment_method": "bank_transfer",
                "created_at": "2024-01-15",
                "paid_at": None
            }
        ]
        
        result = export_payments_csv(payments)
        
        assert result is not None
        assert "id,organization_name,amount,currency,status" in result
        assert "Clinic A" in result
        assert "799" in result
        assert "succeeded" in result
        assert "bank_transfer" in result


@pytest.mark.unit
@pytest.mark.utils
class TestCSVEdgeCases:
    """Test edge cases in CSV export."""
    
    def test_export_with_special_characters(self):
        """Test handling of special characters in data."""
        data = [
            {"name": "Alice, Bob", "description": "Test \"quoted\" value"},
            {"name": "Charlie\nNewline", "description": "Test\ttab"}
        ]
        columns = ["name", "description"]
        
        result = export_to_csv(data, columns)
        
        # CSV should handle special characters
        assert result is not None
        
        # Parse to verify it's still valid CSV
        reader = csv.DictReader(io.StringIO(result))
        rows = list(reader)
        assert len(rows) == 2
    
    def test_export_with_unicode(self):
        """Test handling of Unicode characters."""
        data = [
            {"name": "עברית", "city": "ירושלים"},
            {"name": "中文", "city": "北京"}
        ]
        columns = ["name", "city"]
        
        result = export_to_csv(data, columns)
        
        assert result is not None
        assert "עברית" in result
        assert "中文" in result
    
    def test_export_with_datetime_objects(self):
        """Test handling of datetime objects."""
        now = datetime.utcnow()
        data = [
            {"name": "Alice", "created_at": now}
        ]
        columns = ["name", "created_at"]
        
        result = export_to_csv(data, columns)
        
        # datetime should be converted to string
        assert result is not None
        assert "Alice" in result

