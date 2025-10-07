"""
Action Parser - Extracts suggested actions from agent responses.

IMPORTANT: This parser does NOT decide what actions to suggest.
It only extracts actions that the agent (LLM) already decided to suggest.

The logic is in the agent's reasoning, not in this code!
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def parse_suggested_actions(agent_response: str) -> List[Dict[str, Any]]:
    """
    Parse suggested actions from agent response.
    
    The agent formats suggestions as:
    **Suggested Actions:**
    1. [Action Name] - Description
    2. [Action Name] - Description
    
    This function only extracts and structures them.
    It does NOT decide what to suggest - that's the agent's job!
    
    Args:
        agent_response: The agent's text response
        
    Returns:
        List of action dictionaries
    """
    actions = []
    
    # Find the "Suggested Actions" section
    pattern = r'\*\*Suggested Actions:\*\*\s*\n((?:\d+\.\s+.+\n?)+)'
    match = re.search(pattern, agent_response, re.MULTILINE | re.IGNORECASE)
    
    if not match:
        logger.debug("No suggested actions found in agent response")
        return actions
    
    actions_text = match.group(1)
    logger.info(f"Found suggested actions section: {len(actions_text)} chars")
    
    # Parse each action line
    # Format: "1. [Action Name] - Description" or "1. Action Name - Description"
    action_pattern = r'(\d+)\.\s+\[?([^\]]+?)\]?\s*-\s*(.+?)(?=\n\d+\.|\n*$)'
    
    for line_match in re.finditer(action_pattern, actions_text, re.DOTALL):
        action_num = line_match.group(1)
        action_name = line_match.group(2).strip()
        description = line_match.group(3).strip()
        
        # Determine action type and icon based on keywords
        # This is just UI metadata, not business logic!
        action_type, icon = _determine_action_metadata(action_name)
        
        # Determine priority based on keywords
        # This is just UI hint, not business logic!
        priority = _determine_priority_hint(action_name, description)
        
        action = {
            "id": f"action_{action_num}",
            "label": action_name,
            "description": description,
            "type": action_type,
            "priority": priority,
            "icon": icon
        }
        
        actions.append(action)
        logger.debug(f"Parsed action: {action['label']}")
    
    logger.info(f"Parsed {len(actions)} suggested actions")
    return actions


def _determine_action_metadata(action_name: str) -> tuple:
    """
    Determine action type and icon based on action name.
    
    This is ONLY for UI display, not business logic!
    The agent already decided what action to suggest.
    """
    action_lower = action_name.lower()
    
    # Scheduling actions
    if any(word in action_lower for word in ["schedule", "book", "appointment", "reschedule"]):
        return ("schedule", "Calendar")
    
    # Analysis actions
    elif any(word in action_lower for word in ["analyze", "review", "check", "examine", "investigate"]):
        return ("analyze", "BarChart")
    
    # Communication actions
    elif any(word in action_lower for word in ["contact", "call", "email", "notify", "message"]):
        return ("contact", "Phone")
    
    # Update actions
    elif any(word in action_lower for word in ["update", "edit", "change", "modify", "adjust"]):
        return ("update", "Edit")
    
    # View actions
    elif any(word in action_lower for word in ["view", "see", "show", "display", "open"]):
        return ("view", "Eye")
    
    # Financial actions
    elif any(word in action_lower for word in ["pay", "payment", "invoice", "billing", "pricing", "revenue"]):
        return ("financial", "DollarSign")
    
    # Default
    else:
        return ("action", "Play")


def _determine_priority_hint(action_name: str, description: str) -> str:
    """
    Determine priority hint based on keywords.
    
    This is ONLY a UI hint, not business logic!
    The agent's ordering already indicates priority.
    """
    combined_text = (action_name + " " + description).lower()
    
    # High priority keywords
    if any(word in combined_text for word in [
        "urgent", "critical", "immediate", "emergency", 
        "asap", "now", "today", "must", "required"
    ]):
        return "high"
    
    # Low priority keywords
    elif any(word in combined_text for word in [
        "consider", "review", "optional", "future",
        "eventually", "when possible", "if needed"
    ]):
        return "low"
    
    # Default to medium
    else:
        return "medium"


def remove_suggested_actions_from_text(agent_response: str) -> str:
    """
    Remove the "Suggested Actions" section from agent response text.
    
    This is used to avoid showing the actions twice:
    - Once as formatted text
    - Once as interactive buttons
    
    Args:
        agent_response: The agent's full text response
        
    Returns:
        Response text without the "Suggested Actions" section
    """
    # Remove the entire "Suggested Actions" section
    pattern = r'\*\*Suggested Actions:\*\*\s*\n(?:\d+\.\s+.+\n?)+'
    cleaned_text = re.sub(pattern, '', agent_response, flags=re.MULTILINE | re.IGNORECASE)
    
    # Clean up extra whitespace
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text
