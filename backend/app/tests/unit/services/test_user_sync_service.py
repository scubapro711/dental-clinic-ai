"""
Unit Tests for User Sync Service

Comprehensive tests for user synchronization between PostgreSQL and Odoo.
Tests user creation, syncing, and Odoo integration.

Test Coverage:
- Service initialization
- User creation with Odoo patient
- Getting Odoo partner ID
- Syncing user to Odoo
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4, UUID

from app.services.user_sync_service import UserSyncService


@pytest.fixture
def mock_db():
    """Mock database session"""
    db = Mock()
    db.query = Mock()
    db.add = Mock()
    db.commit = Mock()
    db.refresh = Mock()
    return db


@pytest.fixture
def mock_odoo_client():
    """Mock Odoo client"""
    client = Mock()
    client.create_patient = Mock(return_value=12345)
    client.get_partner_by_email = Mock(return_value=None)
    return client


@pytest.fixture
def user_sync_service(mock_db, mock_odoo_client):
    """User sync service with mocked dependencies"""
    with patch('app.services.user_sync_service.OdooClient', return_value=mock_odoo_client):
        service = UserSyncService(db=mock_db)
        service.odoo = mock_odoo_client
        return service


@pytest.mark.unit
@pytest.mark.services
class TestUserSyncServiceInitialization:
    """Test User Sync Service initialization"""
    
    def test_initialization(self, mock_db):
        """Test service initializes correctly"""
        with patch('app.services.user_sync_service.OdooClient'):
            service = UserSyncService(db=mock_db)
            
            assert service.db == mock_db
            assert service.odoo is not None
    
    def test_initialization_creates_odoo_client(self, mock_db):
        """Test initialization creates Odoo client"""
        with patch('app.services.user_sync_service.OdooClient') as mock_odoo:
            service = UserSyncService(db=mock_db)
            
            mock_odoo.assert_called_once()


@pytest.mark.unit
@pytest.mark.services
class TestCreateUserWithOdooPatient:
    """Test creating user with Odoo patient"""
    
    @patch('app.services.user_sync_service.AuthService')
    def test_create_user_with_odoo_patient_success(
        self,
        mock_auth,
        user_sync_service,
        mock_db
    ):
        """Test successful user creation with Odoo patient"""
        # Mock user and membership
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_membership = Mock()
        
        mock_auth.create_user = Mock(return_value=mock_user)
        
        # Mock query for membership
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        org_id = uuid4()
        user, membership = user_sync_service.create_user_with_odoo_patient(
            email="test@example.com",
            full_name="Test User",
            phone="0501234567",
            organization_id=org_id
        )
        
        # Verify Odoo patient was created
        user_sync_service.odoo.create_patient.assert_called_once()
        
        # Verify user was created
        assert user is not None
        assert membership is not None
    
    @patch('app.services.user_sync_service.AuthService')
    def test_create_user_odoo_patient_called_with_correct_params(
        self,
        mock_auth,
        user_sync_service
    ):
        """Test Odoo patient creation with correct parameters"""
        mock_auth.create_user = Mock(return_value=Mock(id=uuid4()))
        
        user_sync_service.create_user_with_odoo_patient(
            email="john@example.com",
            full_name="John Doe",
            phone="0509876543",
            organization_id=uuid4()
        )
        
        # Verify Odoo was called with correct params
        call_args = user_sync_service.odoo.create_patient.call_args
        assert call_args[1]['name'] == "John Doe"
        assert call_args[1]['email'] == "john@example.com"
        assert call_args[1]['phone'] == "0509876543"
    
    @patch('app.services.user_sync_service.AuthService')
    def test_create_user_with_patient_role(
        self,
        mock_auth,
        user_sync_service,
        mock_db
    ):
        """Test user creation with patient role"""
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_auth.create_user = Mock(return_value=mock_user)
        
        mock_membership = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        user, membership = user_sync_service.create_user_with_odoo_patient(
            email="patient@example.com",
            full_name="Patient Name",
            phone="0501111111",
            organization_id=uuid4(),
            organization_role="patient"
        )
        
        assert user is not None
    
    def test_create_user_odoo_failure(self, user_sync_service):
        """Test handling of Odoo creation failure"""
        user_sync_service.odoo.create_patient.side_effect = Exception("Odoo Error")
        
        with pytest.raises(Exception):
            user_sync_service.create_user_with_odoo_patient(
                email="fail@example.com",
                full_name="Fail User",
                phone="0501234567",
                organization_id=uuid4()
            )


@pytest.mark.unit
@pytest.mark.services
class TestGetOdooPartnerId:
    """Test getting Odoo partner ID"""
    
    def test_get_odoo_partner_id_exists(self, user_sync_service, mock_db):
        """Test getting existing Odoo partner ID"""
        user_id = uuid4()
        org_id = uuid4()
        
        # Mock membership with odoo_partner_id
        mock_membership = Mock()
        mock_membership.odoo_partner_id = 12345
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        partner_id = user_sync_service.get_odoo_partner_id(user_id, org_id)
        
        assert partner_id == 12345
    
    def test_get_odoo_partner_id_not_exists(self, user_sync_service, mock_db):
        """Test getting Odoo partner ID when not exists"""
        user_id = uuid4()
        org_id = uuid4()
        
        # Mock membership without odoo_partner_id
        mock_membership = Mock()
        mock_membership.odoo_partner_id = None
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        partner_id = user_sync_service.get_odoo_partner_id(user_id, org_id)
        
        assert partner_id is None
    
    def test_get_odoo_partner_id_no_membership(self, user_sync_service, mock_db):
        """Test getting Odoo partner ID when membership doesn't exist"""
        user_id = uuid4()
        org_id = uuid4()
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        partner_id = user_sync_service.get_odoo_partner_id(user_id, org_id)
        
        assert partner_id is None


@pytest.mark.unit
@pytest.mark.services
class TestSyncUserToOdoo:
    """Test syncing user to Odoo"""
    
    def test_sync_user_to_odoo_new_patient(self, user_sync_service, mock_db):
        """Test syncing user to Odoo when patient doesn't exist"""
        user_id = uuid4()
        org_id = uuid4()
        
        # Mock user
        mock_user = Mock()
        mock_user.email = "sync@example.com"
        mock_user.full_name = "Sync User"
        mock_user.phone = "0501234567"
        
        # Mock membership without Odoo ID
        mock_membership = Mock()
        mock_membership.odoo_partner_id = None
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_query.get.return_value = mock_user
        mock_db.query.return_value = mock_query
        
        # Mock Odoo client
        user_sync_service.odoo.create_patient.return_value = 54321
        
        partner_id = user_sync_service.sync_user_to_odoo(user_id, org_id)
        
        assert partner_id == 54321
        user_sync_service.odoo.create_patient.assert_called_once()
    
    def test_sync_user_to_odoo_existing_patient(self, user_sync_service, mock_db):
        """Test syncing user to Odoo when patient already exists"""
        user_id = uuid4()
        org_id = uuid4()
        
        # Mock membership with existing Odoo ID
        mock_membership = Mock()
        mock_membership.odoo_partner_id = 99999
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        partner_id = user_sync_service.sync_user_to_odoo(user_id, org_id)
        
        # Should return existing ID without creating new patient
        assert partner_id == 99999
        user_sync_service.odoo.create_patient.assert_not_called()
    
    def test_sync_user_to_odoo_no_membership(self, user_sync_service, mock_db):
        """Test syncing user when membership doesn't exist"""
        user_id = uuid4()
        org_id = uuid4()
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        with pytest.raises(Exception):
            user_sync_service.sync_user_to_odoo(user_id, org_id)


@pytest.mark.unit
@pytest.mark.services
class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch('app.services.user_sync_service.AuthService')
    def test_create_user_empty_phone(self, mock_auth, user_sync_service, mock_db):
        """Test creating user with empty phone"""
        mock_user = Mock()
        mock_user.id = uuid4()
        mock_auth.create_user = Mock(return_value=mock_user)
        
        mock_membership = Mock()
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_membership
        mock_db.query.return_value = mock_query
        
        user, membership = user_sync_service.create_user_with_odoo_patient(
            email="test@example.com",
            full_name="Test User",
            phone="",
            organization_id=uuid4()
        )
        
        assert user is not None

