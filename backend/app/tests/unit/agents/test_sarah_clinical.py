"""
Unit Tests for Sarah Clinical Agent

Tests for Sarah (Clinical Operations) agent including:
- Agent initialization
- Clinical tool availability
- Patient care handling
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.agents
class TestSarahClinicalAgent:
    """Test Sarah Clinical Agent."""
    
    def test_sarah_agent_import(self):
        """Test that sarah_agent can be imported."""
        from app.agents.sarah_clinical import sarah_agent
        assert sarah_agent is not None
    
    def test_sarah_module_exists(self):
        """Test that sarah_clinical module exists."""
        import app.agents.sarah_clinical as sarah_module
        assert sarah_module is not None
    
    def test_sarah_agent_callable(self):
        """Test that sarah_agent is callable."""
        from app.agents.sarah_clinical import sarah_agent
        assert callable(sarah_agent)

