"""
MCP Client Wrapper

Wrapper for Model Context Protocol (MCP) clients.
Provides a Python interface to MCP servers (Stripe, etc.)
"""

import json
import subprocess
from typing import Any, Dict, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass


class MCPClient:
    """
    MCP Client Wrapper
    
    Provides a Python interface to interact with MCP servers via manus-mcp-cli.
    
    Usage:
        client = MCPClient(server="stripe")
        result = client.call_tool("create_customer", {
            "email": "clinic@example.com",
            "name": "Demo Clinic"
        })
    """
    
    def __init__(self, server: str):
        """
        Initialize MCP Client
        
        Args:
            server: MCP server name (e.g., "stripe")
        """
        self.server = server
        self.cli_command = "manus-mcp-cli"
    
    def call_tool(
        self,
        tool_name: str,
        input_data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Call an MCP tool
        
        Args:
            tool_name: Name of the tool to call
            input_data: Input data for the tool (will be JSON-serialized)
            timeout: Timeout in seconds
        
        Returns:
            Tool output as a dictionary
        
        Raises:
            MCPClientError: If the tool call fails
        """
        try:
            # Build command
            cmd = [
                self.cli_command,
                "tool",
                "call",
                tool_name,
                "--server",
                self.server
            ]
            
            # Add input data if provided
            if input_data:
                cmd.extend(["--input", json.dumps(input_data)])
            
            # Execute command
            logger.info(f"Calling MCP tool: {tool_name} on server {self.server}")
            logger.debug(f"Input data: {input_data}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True
            )
            
            # Parse output
            output = result.stdout.strip()
            logger.debug(f"MCP tool output: {output}")
            
            # Try to parse as JSON
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If not JSON, return as text
                return {"output": output, "raw": True}
        
        except subprocess.TimeoutExpired as e:
            logger.error(f"MCP tool call timed out: {tool_name}")
            raise MCPClientError(f"Tool call timed out after {timeout}s: {tool_name}") from e
        
        except subprocess.CalledProcessError as e:
            logger.error(f"MCP tool call failed: {tool_name}")
            logger.error(f"Error output: {e.stderr}")
            raise MCPClientError(f"Tool call failed: {tool_name}\n{e.stderr}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error calling MCP tool: {tool_name}")
            logger.error(f"Error: {str(e)}")
            raise MCPClientError(f"Unexpected error: {str(e)}") from e
    
    def list_tools(self) -> list[Dict[str, Any]]:
        """
        List available tools on the MCP server
        
        Returns:
            List of tool definitions
        
        Raises:
            MCPClientError: If the listing fails
        """
        try:
            cmd = [
                self.cli_command,
                "tool",
                "list",
                "--server",
                self.server
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
                check=True
            )
            
            output = result.stdout.strip()
            
            # Parse tool list (format may vary)
            # For now, return raw output
            return {"tools": output, "raw": True}
        
        except Exception as e:
            logger.error(f"Failed to list tools on server {self.server}")
            raise MCPClientError(f"Failed to list tools: {str(e)}") from e


# Singleton instances for common servers
_stripe_client: Optional[MCPClient] = None


def get_stripe_client() -> MCPClient:
    """
    Get singleton Stripe MCP client
    
    Returns:
        MCPClient configured for Stripe
    """
    global _stripe_client
    if _stripe_client is None:
        _stripe_client = MCPClient(server="stripe")
    return _stripe_client

