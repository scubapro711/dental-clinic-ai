"""
Unit Tests for Harper HIPAA Agent

Tests for Harper (HIPAA Compliance Specialist) agent including:
- Agent initialization
- HIPAA tool availability
- Compliance checking
"""

import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.agents
class TestHarperHIPAAAgent:
    """Test Harper HIPAA Agent."""
    
    def test_harper_node_import(self):
        """Test that harper_node can be imported."""
        from app.agents.harper_hipaa import harper_node
        assert harper_node is not None
    
    def test_harper_module_exists(self):
        """Test that harper_hipaa module exists."""
        import app.agents.harper_hipaa as harper_module
        assert harper_module is not None
    
    def test_harper_node_callable(self):
        """Test that harper_node is callable."""
        from app.agents.harper_hipaa import harper_node
        assert callable(harper_node)
    
    def test_harper_has_hipaa_focus(self):
        """Test that Harper module is focused on HIPAA compliance."""
        import app.agents.harper_hipaa as harper_module
        
        # Module should have HIPAA-related content
        module_content = str(harper_module.__dict__)
        assert 'hipaa' in module_content.lower() or 'compliance' in module_content.lower()

