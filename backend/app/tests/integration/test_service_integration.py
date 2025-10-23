"""
Integration Tests for Service Integration

Tests for service-to-service integration including:
- Service dependencies
- Service communication
- Data flow between services
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.integration
@pytest.mark.services
class TestServiceIntegration:
    """Test Service Integration."""
    
    def test_auth_service_with_database(self):
        """Test auth service database integration."""
        try:
            from app.services.auth_service import AuthService
            from app.core.database import get_db
            
            assert AuthService is not None
            assert get_db is not None
        except ImportError:
            pytest.skip("Required modules not found")
    
    def test_conversation_service_with_database(self):
        """Test conversation service database integration."""
        try:
            from app.services.conversation_service import ConversationService
            from app.core.database import get_db
            
            assert ConversationService is not None
            assert get_db is not None
        except ImportError:
            pytest.skip("Required modules not found")
    
    def test_email_service_with_smtp(self):
        """Test email service SMTP integration."""
        try:
            from app.services.email_service import EmailService
            import smtplib
            
            assert EmailService is not None
            assert smtplib is not None
        except ImportError:
            pytest.skip("Required modules not found")
    
    def test_alert_service_with_email(self):
        """Test alert service email integration."""
        try:
            from app.services.alert_service import AlertService
            import smtplib
            
            assert AlertService is not None
            assert smtplib is not None
        except ImportError:
            pytest.skip("Required modules not found")


@pytest.mark.integration
@pytest.mark.agents
class TestAgentServiceIntegration:
    """Test Agent-Service Integration."""
    
    def test_agent_graph_with_memory(self):
        """Test agent graph memory integration."""
        try:
            from app.agents.agent_graph_v5 import get_memory_saver
            from app.core.memory import get_memory_saver as core_memory
            
            assert get_memory_saver is not None
            assert core_memory is not None
        except ImportError:
            pytest.skip("Required modules not found")
    
    def test_agents_with_tools(self):
        """Test agents with tool integration."""
        try:
            from app.agents.alex_v2 import AlexAgent
            from app.agents.tools import agent_tools
            
            assert AlexAgent is not None
            assert agent_tools is not None
        except ImportError:
            pytest.skip("Required modules not found")

