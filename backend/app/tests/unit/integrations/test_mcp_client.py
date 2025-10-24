"""
Unit Tests for MCP Client

Tests for app.integrations.mcp_client module including:
- MCPClient class
- Tool calling functionality
- Error handling
- Singleton pattern for Stripe client
"""

import pytest
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock

from app.integrations.mcp_client import (
    MCPClient,
    MCPClientError,
    get_stripe_client,
)


@pytest.mark.unit
@pytest.mark.integration
class TestMCPClient:
    """Test MCPClient class."""
    
    def test_init(self):
        """Test MCPClient initialization."""
        client = MCPClient(server="stripe")
        
        assert client.server == "stripe"
        assert client.cli_command == "manus-mcp-cli"
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_success_json(self, mock_run):
        """Test successful tool call with JSON response."""
        # Mock subprocess response
        mock_result = Mock()
        mock_result.stdout = '{"customer_id": "cus_123", "status": "active"}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = MCPClient(server="stripe")
        result = client.call_tool("create_customer", {"email": "test@example.com"})
        
        assert result == {"customer_id": "cus_123", "status": "active"}
        
        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "manus-mcp-cli"
        assert call_args[0][0][1] == "tool"
        assert call_args[0][0][2] == "call"
        assert call_args[0][0][3] == "create_customer"
        assert "--server" in call_args[0][0]
        assert "stripe" in call_args[0][0]
        assert "--input" in call_args[0][0]
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_success_text(self, mock_run):
        """Test successful tool call with non-JSON response."""
        # Mock subprocess response with non-JSON text
        mock_result = Mock()
        mock_result.stdout = "Tool executed successfully"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = MCPClient(server="test")
        result = client.call_tool("some_tool")
        
        assert result == {"output": "Tool executed successfully", "raw": True}
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_without_input(self, mock_run):
        """Test tool call without input data."""
        mock_result = Mock()
        mock_result.stdout = '{"result": "ok"}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = MCPClient(server="test")
        result = client.call_tool("list_items")
        
        assert result == {"result": "ok"}
        
        # Verify --input was not included
        call_args = mock_run.call_args[0][0]
        assert "--input" not in call_args
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_timeout(self, mock_run):
        """Test tool call timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["manus-mcp-cli"], timeout=30
        )
        
        client = MCPClient(server="test")
        
        with pytest.raises(MCPClientError) as exc_info:
            client.call_tool("slow_tool", timeout=30)
        
        assert "timed out" in str(exc_info.value).lower()
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_process_error(self, mock_run):
        """Test tool call with process error."""
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["manus-mcp-cli"],
            stderr="Tool not found"
        )
        
        client = MCPClient(server="test")
        
        with pytest.raises(MCPClientError) as exc_info:
            client.call_tool("invalid_tool")
        
        assert "failed" in str(exc_info.value).lower()
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_unexpected_error(self, mock_run):
        """Test tool call with unexpected error."""
        mock_run.side_effect = Exception("Unexpected error")
        
        client = MCPClient(server="test")
        
        with pytest.raises(MCPClientError) as exc_info:
            client.call_tool("some_tool")
        
        assert "unexpected" in str(exc_info.value).lower()
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_custom_timeout(self, mock_run):
        """Test tool call with custom timeout."""
        mock_result = Mock()
        mock_result.stdout = '{"result": "ok"}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = MCPClient(server="test")
        client.call_tool("some_tool", timeout=60)
        
        # Verify timeout was passed to subprocess
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs['timeout'] == 60
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_call_tool_with_complex_input(self, mock_run):
        """Test tool call with complex nested input data."""
        mock_result = Mock()
        mock_result.stdout = '{"success": true}'
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        complex_input = {
            "customer": {
                "email": "test@example.com",
                "metadata": {
                    "clinic_id": "123",
                    "plan": "premium"
                }
            },
            "items": [
                {"id": 1, "quantity": 2},
                {"id": 2, "quantity": 1}
            ]
        }
        
        client = MCPClient(server="stripe")
        result = client.call_tool("create_subscription", complex_input)
        
        assert result == {"success": True}
        
        # Verify input was JSON-serialized
        call_args = mock_run.call_args[0][0]
        input_index = call_args.index("--input") + 1
        input_json = call_args[input_index]
        assert json.loads(input_json) == complex_input


@pytest.mark.unit
@pytest.mark.integration
class TestMCPClientListTools:
    """Test MCPClient list_tools method."""
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_list_tools_success(self, mock_run):
        """Test successful tool listing."""
        mock_result = Mock()
        mock_result.stdout = "Available tools:\n1. create_customer\n2. list_customers"
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = MCPClient(server="stripe")
        result = client.list_tools()
        
        assert "tools" in result
        assert result["raw"] is True
        
        # Verify correct command
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "manus-mcp-cli"
        assert call_args[1] == "tool"
        assert call_args[2] == "list"
        assert "--server" in call_args
        assert "stripe" in call_args
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_list_tools_error(self, mock_run):
        """Test tool listing error."""
        mock_run.side_effect = Exception("Connection failed")
        
        client = MCPClient(server="test")
        
        with pytest.raises(MCPClientError) as exc_info:
            client.list_tools()
        
        assert "failed to list tools" in str(exc_info.value).lower()
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_list_tools_timeout(self, mock_run):
        """Test tool listing with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd=["manus-mcp-cli"], timeout=10
        )
        
        client = MCPClient(server="test")
        
        with pytest.raises(MCPClientError):
            client.list_tools()


@pytest.mark.unit
@pytest.mark.integration
class TestMCPClientSingleton:
    """Test singleton pattern for Stripe client."""
    
    def test_get_stripe_client_singleton(self):
        """Test that get_stripe_client returns singleton instance."""
        # Reset singleton
        import app.integrations.mcp_client as mcp_module
        mcp_module._stripe_client = None
        
        client1 = get_stripe_client()
        client2 = get_stripe_client()
        
        assert client1 is client2
        assert client1.server == "stripe"
    
    def test_get_stripe_client_creates_new_if_none(self):
        """Test that get_stripe_client creates new instance if None."""
        import app.integrations.mcp_client as mcp_module
        mcp_module._stripe_client = None
        
        client = get_stripe_client()
        
        assert client is not None
        assert isinstance(client, MCPClient)
        assert client.server == "stripe"
    
    def test_get_stripe_client_reuses_existing(self):
        """Test that get_stripe_client reuses existing instance."""
        import app.integrations.mcp_client as mcp_module
        
        # Create a mock client
        mock_client = MCPClient(server="stripe")
        mcp_module._stripe_client = mock_client
        
        client = get_stripe_client()
        
        assert client is mock_client


@pytest.mark.unit
@pytest.mark.integration
class TestMCPClientError:
    """Test MCPClientError exception."""
    
    def test_mcp_client_error_is_exception(self):
        """Test that MCPClientError is an Exception."""
        error = MCPClientError("Test error")
        
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
    
    def test_mcp_client_error_with_cause(self):
        """Test MCPClientError with cause."""
        original_error = ValueError("Original error")
        
        try:
            raise MCPClientError("Wrapped error") from original_error
        except MCPClientError as e:
            assert str(e) == "Wrapped error"
            assert e.__cause__ is original_error


@pytest.mark.unit
@pytest.mark.integration
class TestMCPClientIntegration:
    """Integration-style tests for MCPClient."""
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_full_workflow_create_customer(self, mock_run):
        """Test full workflow of creating a customer via Stripe MCP."""
        # Mock successful customer creation
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "id": "cus_123456",
            "email": "clinic@example.com",
            "name": "Demo Clinic",
            "created": 1234567890
        })
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        client = get_stripe_client()
        result = client.call_tool("create_customer", {
            "email": "clinic@example.com",
            "name": "Demo Clinic"
        })
        
        assert result["id"] == "cus_123456"
        assert result["email"] == "clinic@example.com"
        assert result["name"] == "Demo Clinic"
    
    @patch('app.integrations.mcp_client.subprocess.run')
    def test_error_handling_chain(self, mock_run):
        """Test error handling through the full chain."""
        # Simulate a process error
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd=["manus-mcp-cli", "tool", "call", "invalid_tool"],
            stderr="Error: Tool 'invalid_tool' not found"
        )
        
        client = MCPClient(server="stripe")
        
        with pytest.raises(MCPClientError) as exc_info:
            client.call_tool("invalid_tool")
        
        error_msg = str(exc_info.value)
        assert "failed" in error_msg.lower()
        assert "invalid_tool" in error_msg

