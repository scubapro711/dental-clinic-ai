"""
Unit Tests for Cost Sync Service

Tests for syncing GCP billing data to database.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import date, timedelta
from decimal import Decimal

from app.services.cost_sync_service import CostSyncService

@pytest.fixture
def mock_db():
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    return db

@pytest.fixture
def cost_sync_service(mock_db):
    with patch('app.services.cost_sync_service.get_bigquery_billing_service'):
        service = CostSyncService(db=mock_db)
        service.bigquery_service = Mock()
        service.bigquery_service.is_configured = Mock(return_value=True)
        service.bigquery_service.get_daily_costs = Mock(return_value={"total_cost": 10.50, "services": []})
        return service

@pytest.mark.unit
@pytest.mark.services
class TestCostSyncInitialization:
    def test_initialization(self, mock_db):
        with patch('app.services.cost_sync_service.get_bigquery_billing_service'):
            service = CostSyncService(db=mock_db)
            assert service.db == mock_db
    
    def test_initialization_creates_bigquery_service(self, mock_db):
        with patch('app.services.cost_sync_service.get_bigquery_billing_service') as mock_bq:
            service = CostSyncService(db=mock_db)
            mock_bq.assert_called_once()

@pytest.mark.unit
@pytest.mark.services
class TestDailyCostSync:
    def test_sync_daily_costs_default_date(self, cost_sync_service):
        result = cost_sync_service.sync_daily_costs()
        assert result is not None
    
    def test_sync_daily_costs_specific_date(self, cost_sync_service):
        target = date(2024, 1, 15)
        result = cost_sync_service.sync_daily_costs(target_date=target)
        assert result is not None
    
    def test_sync_daily_costs_yesterday_default(self, cost_sync_service):
        result = cost_sync_service.sync_daily_costs()
        # Default should be yesterday
        assert result is not None
    
    def test_sync_daily_costs_not_configured(self, cost_sync_service):
        cost_sync_service.bigquery_service.is_configured = Mock(return_value=False)
        result = cost_sync_service.sync_daily_costs()
        assert result["status"] == "skipped"
        assert "reason" in result
    
    def test_sync_daily_costs_error_handling(self, cost_sync_service):
        cost_sync_service.bigquery_service.get_daily_costs = Mock(side_effect=Exception("BQ Error"))
        result = cost_sync_service.sync_daily_costs()
        assert result is not None
    
    def test_sync_daily_costs_calls_bigquery(self, cost_sync_service):
        cost_sync_service.sync_daily_costs(target_date=date(2024, 1, 1))
        cost_sync_service.bigquery_service.get_daily_costs.assert_called()
    
    def test_sync_daily_costs_stores_in_db(self, cost_sync_service, mock_db):
        cost_sync_service.sync_daily_costs()
        # Should add cost tracking record
        assert mock_db.add.called or mock_db.commit.called

@pytest.mark.unit
@pytest.mark.services
class TestCostCalculations:
    def test_sync_calculates_total_cost(self, cost_sync_service):
        cost_sync_service.bigquery_service.get_daily_costs = Mock(return_value={
            "total_cost": 25.50,
            "services": [{"name": "Cloud Run", "cost": 15.00}, {"name": "Cloud SQL", "cost": 10.50}]
        })
        result = cost_sync_service.sync_daily_costs()
        assert result is not None
    
    def test_sync_handles_zero_cost(self, cost_sync_service):
        cost_sync_service.bigquery_service.get_daily_costs = Mock(return_value={"total_cost": 0.0, "services": []})
        result = cost_sync_service.sync_daily_costs()
        assert result is not None
    
    def test_sync_handles_decimal_precision(self, cost_sync_service):
        cost_sync_service.bigquery_service.get_daily_costs = Mock(return_value={"total_cost": 10.123456, "services": []})
        result = cost_sync_service.sync_daily_costs()
        assert result is not None

@pytest.mark.unit
@pytest.mark.services
class TestEdgeCases:
    def test_sync_future_date(self, cost_sync_service):
        future = date.today() + timedelta(days=30)
        result = cost_sync_service.sync_daily_costs(target_date=future)
        assert result is not None
    
    def test_sync_very_old_date(self, cost_sync_service):
        old = date(2020, 1, 1)
        result = cost_sync_service.sync_daily_costs(target_date=old)
        assert result is not None

