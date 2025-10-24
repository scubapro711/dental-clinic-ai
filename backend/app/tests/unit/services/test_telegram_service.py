"""
Unit Tests for Telegram Service

Tests for app.services.telegram_service module including:
- TelegramService class methods
- User creation and management
- Patient linking
- Invite code validation
- Conversation management
- Onboarding status
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.telegram_service import TelegramService
from app.models.telegram_user import TelegramUser, TelegramUserStatus
from app.models.telegram_conversation import TelegramConversation
from app.models.telegram_invite_code import TelegramInviteCode, InviteCodeStatus

# Note: Service code now uses EXHAUSTED (bug fixed)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = MagicMock()
    db.query = MagicMock()
    db.add = MagicMock()
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.rollback = MagicMock()
    return db


@pytest.fixture
def mock_odoo_client():
    """Create mock Odoo client."""
    with patch('app.services.telegram_service.OdooClient') as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def telegram_service(mock_db, mock_odoo_client):
    """Create TelegramService instance with mocked dependencies."""
    service = TelegramService(mock_db)
    service.odoo_client = mock_odoo_client
    return service


@pytest.fixture
def sample_telegram_user():
    """Create sample TelegramUser."""
    return TelegramUser(
        id=uuid4(),
        telegram_user_id=123456789,
        telegram_username="testuser",
        telegram_first_name="Test",
        telegram_last_name="User",
        organization_id="00000000-0000-0000-0000-000000000000",
        status=TelegramUserStatus.NEW,
    )


@pytest.mark.unit
@pytest.mark.service
class TestTelegramServiceGetOrCreateUser:
    """Test get_or_create_user method."""
    
    def test_get_existing_user(self, telegram_service, mock_db, sample_telegram_user):
        """Test getting existing user without updates."""
        # Setup mock to return existing user
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_telegram_user
        
        result = telegram_service.get_or_create_user(
            telegram_id=123456789,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        
        assert result == sample_telegram_user
        mock_db.commit.assert_not_called()  # No updates needed
    
    def test_get_existing_user_with_updates(self, telegram_service, mock_db, sample_telegram_user):
        """Test getting existing user and updating changed fields."""
        # Setup mock to return existing user
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_telegram_user
        
        result = telegram_service.get_or_create_user(
            telegram_id=123456789,
            username="newusername",  # Changed
            first_name="NewFirst",    # Changed
            last_name="User"
        )
        
        assert result.telegram_username == "newusername"
        assert result.telegram_first_name == "NewFirst"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_create_new_user(self, telegram_service, mock_db):
        """Test creating new user when not exists."""
        # Setup mock to return None (user doesn't exist)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        result = telegram_service.get_or_create_user(
            telegram_id=987654321,
            username="newuser",
            first_name="New",
            last_name="User"
        )
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.service
class TestTelegramServiceLinkToPatient:
    """Test link_to_patient method."""
    
    def test_link_to_patient_success(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test successfully linking Telegram user to patient."""
        # Setup mock Odoo client to return patient
        mock_odoo_client.search_patients.return_value = [
            {"id": 123, "name": "Test Patient", "phone": "+1234567890"}
        ]
        
        result = telegram_service.link_to_patient(
            telegram_user=sample_telegram_user,
            patient_phone="+1234567890",
            organization_id="org-123"
        )
        
        assert result is True
        assert sample_telegram_user.patient_id == 123
        assert sample_telegram_user.organization_id == "org-123"
        assert sample_telegram_user.status == TelegramUserStatus.LINKED
        mock_db.commit.assert_called_once()
    
    def test_link_to_patient_not_found(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test linking when patient not found in Odoo."""
        # Setup mock Odoo client to return empty list
        mock_odoo_client.search_patients.return_value = []
        
        result = telegram_service.link_to_patient(
            telegram_user=sample_telegram_user,
            patient_phone="+1234567890",
            organization_id="org-123"
        )
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_link_to_patient_error(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test linking when Odoo client raises exception."""
        # Setup mock Odoo client to raise exception
        mock_odoo_client.search_patients.side_effect = Exception("Odoo error")
        
        result = telegram_service.link_to_patient(
            telegram_user=sample_telegram_user,
            patient_phone="+1234567890",
            organization_id="org-123"
        )
        
        assert result is False
        mock_db.rollback.assert_called_once()


@pytest.mark.unit
@pytest.mark.service
class TestTelegramServiceCreatePatientAndLink:
    """Test create_patient_and_link method."""
    
    def test_create_patient_and_link_success(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test successfully creating patient and linking."""
        # Setup mock Odoo client to return patient ID
        mock_odoo_client.create_patient.return_value = 456
        
        patient_data = {
            "name": "New Patient",
            "phone": "+9876543210",
            "email": "patient@example.com",
            "birth_date": "1990-01-01"
        }
        
        result = telegram_service.create_patient_and_link(
            telegram_user=sample_telegram_user,
            patient_data=patient_data,
            organization_id="org-456"
        )
        
        assert result is True
        assert sample_telegram_user.patient_id == 456
        assert sample_telegram_user.organization_id == "org-456"
        assert sample_telegram_user.status == TelegramUserStatus.LINKED
        mock_db.commit.assert_called_once()
    
    def test_create_patient_and_link_odoo_fails(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test when Odoo fails to create patient."""
        # Setup mock Odoo client to return None (failure)
        mock_odoo_client.create_patient.return_value = None
        
        patient_data = {
            "name": "New Patient",
            "phone": "+9876543210"
        }
        
        result = telegram_service.create_patient_and_link(
            telegram_user=sample_telegram_user,
            patient_data=patient_data,
            organization_id="org-456"
        )
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_create_patient_and_link_error(self, telegram_service, mock_db, mock_odoo_client, sample_telegram_user):
        """Test when exception occurs during creation."""
        # Setup mock Odoo client to raise exception
        mock_odoo_client.create_patient.side_effect = Exception("Odoo error")
        
        patient_data = {
            "name": "New Patient",
            "phone": "+9876543210"
        }
        
        result = telegram_service.create_patient_and_link(
            telegram_user=sample_telegram_user,
            patient_data=patient_data,
            organization_id="org-456"
        )
        
        assert result is False
        mock_db.rollback.assert_called_once()


@pytest.mark.unit
@pytest.mark.service
@patch('app.services.telegram_service.TelegramInviteCode')
class TestTelegramServiceValidateInviteCode:
    """Test validate_invite_code method."""
    
    def test_validate_invite_code_success(self, mock_invite_model, telegram_service, mock_db, sample_telegram_user):
        """Test successfully validating and using invite code."""
        # Create mock invite code (using Mock to avoid model field issues)
        invite = Mock()
        invite.id = uuid4()
        invite.code = "INVITE123"
        invite.organization_id = "org-789"
        invite.status = InviteCodeStatus.ACTIVE
        invite.max_uses = 10
        invite.used_count = 5
        invite.expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Setup mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = invite
        
        result = telegram_service.validate_invite_code("INVITE123", sample_telegram_user)
        
        assert result == invite
        assert invite.used_count == 6
        assert sample_telegram_user.organization_id == "org-789"
        mock_db.commit.assert_called_once()
    
    def test_validate_invite_code_not_found(self, mock_invite_model, telegram_service, mock_db, sample_telegram_user):
        """Test validating non-existent invite code."""
        # Setup mock query to return None
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        result = telegram_service.validate_invite_code("INVALID", sample_telegram_user)
        
        assert result is None
    
    def test_validate_invite_code_expired(self, mock_invite_model, telegram_service, mock_db, sample_telegram_user):
        """Test validating expired invite code."""
        # Create expired invite code (using Mock)
        invite = Mock()
        invite.id = uuid4()
        invite.code = "EXPIRED123"
        invite.organization_id = "org-789"
        invite.status = InviteCodeStatus.ACTIVE
        invite.expires_at = datetime.utcnow() - timedelta(days=1)  # Expired
        
        # Setup mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = invite
        
        result = telegram_service.validate_invite_code("EXPIRED123", sample_telegram_user)
        
        assert result is None
        assert invite.status == InviteCodeStatus.EXPIRED
    
    def test_validate_invite_code_max_uses_reached(self, mock_invite_model, telegram_service, mock_db, sample_telegram_user):
        """Test validating invite code that reached max uses."""
        # Create invite code at max uses (using Mock)
        invite = Mock()
        invite.id = uuid4()
        invite.code = "MAXED123"
        invite.organization_id = "org-789"
        invite.status = InviteCodeStatus.ACTIVE
        invite.max_uses = 5
        invite.used_count = 5  # Already at max
        invite.expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Setup mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = invite
        
        result = telegram_service.validate_invite_code("MAXED123", sample_telegram_user)
        
        assert result is None
        assert invite.status == InviteCodeStatus.EXHAUSTED
    
    def test_validate_invite_code_marks_used_when_reaching_max(self, mock_invite_model, telegram_service, mock_db, sample_telegram_user):
        """Test that invite code is marked as USED when reaching max uses."""
        # Create invite code one use away from max (using Mock)
        invite = Mock()
        invite.id = uuid4()
        invite.code = "LASTONE123"
        invite.organization_id = "org-789"
        invite.status = InviteCodeStatus.ACTIVE
        invite.max_uses = 5
        invite.used_count = 4  # One more use available
        invite.expires_at = datetime.utcnow() + timedelta(days=30)
        
        # Setup mock query
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = invite
        
        result = telegram_service.validate_invite_code("LASTONE123", sample_telegram_user)
        
        assert result == invite
        assert invite.used_count == 5
        assert invite.status == InviteCodeStatus.EXHAUSTED


@pytest.mark.unit
@pytest.mark.service
@patch('app.services.telegram_service.TelegramConversation')
class TestTelegramServiceGetOrCreateConversation:
    """Test get_or_create_conversation method."""
    
    def test_get_existing_conversation(self, mock_conversation_model, telegram_service, mock_db, sample_telegram_user):
        """Test getting existing conversation."""
        # Create mock conversation (using Mock to avoid model field issues)
        conversation = Mock()
        conversation.id = uuid4()
        conversation.telegram_user_id = sample_telegram_user.id
        conversation.organization_id = sample_telegram_user.organization_id
        conversation.conversation_id = uuid4()
        
        # Setup mock query with order_by
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = conversation
        
        result = telegram_service.get_or_create_conversation(sample_telegram_user, 111222333)
        
        assert result == conversation
        mock_db.add.assert_not_called()
    
    def test_create_new_conversation(self, mock_conversation_model, telegram_service, mock_db, sample_telegram_user):
        """Test creating new conversation when none exists."""
        # Setup mock query to return None (with order_by)
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        
        result = telegram_service.get_or_create_conversation(sample_telegram_user, 444555666)
        
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()


@pytest.mark.unit
@pytest.mark.service
class TestTelegramServiceOnboardingStatus:
    """Test onboarding status methods."""
    
    def test_get_onboarding_status_new_user(self, telegram_service):
        """Test onboarding status for new user."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.NEW,
            organization_id=None,
            patient_id=None
        )
        
        status = telegram_service.get_onboarding_status(user)
        
        assert status["status"] == TelegramUserStatus.NEW
        assert status["has_organization"] is False
        assert status["has_patient_link"] is False
        assert status["is_complete"] is False
        assert status["next_step"] == "need_invite_code"
    
    def test_get_onboarding_status_has_org(self, telegram_service):
        """Test onboarding status for user with organization."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.PENDING,  # Use valid status from enum
            organization_id="org-123",
            patient_id=None
        )
        
        status = telegram_service.get_onboarding_status(user)
        
        assert status["has_organization"] is True
        assert status["has_patient_link"] is False
        assert status["next_step"] == "need_patient_link"
    
    def test_get_onboarding_status_linked(self, telegram_service):
        """Test onboarding status for fully linked user."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.LINKED,
            organization_id="org-123",
            patient_id=456
        )
        
        status = telegram_service.get_onboarding_status(user)
        
        assert status["status"] == TelegramUserStatus.LINKED
        assert status["has_organization"] is True
        assert status["has_patient_link"] is True
        assert status["is_complete"] is True
        assert status["next_step"] == "complete"
    
    def test_get_next_onboarding_step_linked(self, telegram_service):
        """Test _get_next_onboarding_step for linked user."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.LINKED,
            organization_id="org-123",
            patient_id=456
        )
        
        next_step = telegram_service._get_next_onboarding_step(user)
        
        assert next_step == "complete"
    
    def test_get_next_onboarding_step_no_org(self, telegram_service):
        """Test _get_next_onboarding_step for user without organization."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.NEW,
            organization_id=None,
            patient_id=None
        )
        
        next_step = telegram_service._get_next_onboarding_step(user)
        
        assert next_step == "need_invite_code"
    
    def test_get_next_onboarding_step_no_patient(self, telegram_service):
        """Test _get_next_onboarding_step for user without patient link."""
        user = TelegramUser(
            telegram_user_id=123,
            status=TelegramUserStatus.PENDING,  # Use valid status from enum
            organization_id="org-123",
            patient_id=None
        )
        
        next_step = telegram_service._get_next_onboarding_step(user)
        
        assert next_step == "need_patient_link"

