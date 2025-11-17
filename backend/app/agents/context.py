"""
DentaFlow Agent Context

This module defines the runtime context that is injected into agent tools.
It provides organization_id, user_id, and user_role without exposing them to the LLM.

This follows LangChain's official ToolRuntime pattern:
https://docs.langchain.com/oss/python/langchain/tools#context
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DentaFlowContext:
    """
    Runtime context for DentaFlow agent tools.
    
    This context is automatically injected into tools via ToolRuntime,
    without being exposed to the LLM or included in the tool schema.
    
    Attributes:
        organization_id: The ID of the organization (tenant/clinic) making the request
        user_id: The ID of the user making the request
        user_role: The role of the user (patient, doctor, admin, etc.)
    """
    organization_id: Optional[str] = None  # None means use default Odoo credentials
    user_id: Optional[str] = None
    user_role: Optional[str] = "patient"
