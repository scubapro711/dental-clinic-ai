import pytest
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append("/home/ubuntu/dental-clinic-ai")
from src.ai_agents.tools.advanced_dental_tool import AdvancedDentalTool

@pytest.fixture
def tool():
    # Set the adapter mode to OPEN_DENTAL for these tests
    with patch.dict(os.environ, {"ADAPTER_MODE": "OPEN_DENTAL"}):
        yield AdvancedDentalTool()

@pytest.mark.asyncio
async def test_search_patients_with_open_dental(tool):
    """Test searching for patients using the Open Dental adapter."""
    with patch("src.ai_agents.tools.open_dental_adapter.OpenDentalAPIClient") as MockAPIClient:
        mock_instance = MockAPIClient.return_value
        mock_instance.get_patients.return_value = [
            {"FName": "John", "LName": "Doe", "Age": 35}
        ]

        # Re-initialize the tool inside the patch context to use the mock
        tool.adapter.client = mock_instance

        result = await tool.search_patients("Doe")
        assert "John Doe" in result
        assert "35" in result

@pytest.mark.asyncio
async def test_get_providers_with_open_dental(tool):
    """Test getting providers using the Open Dental adapter."""
    with patch("src.ai_agents.tools.open_dental_adapter.OpenDentalAPIClient") as MockAPIClient:
        mock_instance = MockAPIClient.return_value
        mock_instance.get_providers.return_value = [
            {"ProvNum": 1, "FName": "John", "LName": "Smith"}
        ]

        # Re-initialize the tool inside the patch context to use the mock
        tool.adapter.client = mock_instance

        result = await tool.get_providers()
        assert "John Smith" in result

