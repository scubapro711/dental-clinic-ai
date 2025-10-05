"""
Fallback Action Generator

When the LLM doesn't provide suggested actions, this module generates
contextual actions based on the conversation intent.

This ensures 100% of responses include suggested actions.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def generate_fallback_actions(user_message: str, agent_response: str) -> List[Dict[str, Any]]:
    """
    Generate fallback suggested actions when LLM doesn't provide them.
    
    Args:
        user_message: The user's last message
        agent_response: The agent's response
        
    Returns:
        List of suggested actions
    """
    user_lower = user_message.lower()
    response_lower = agent_response.lower()
    
    # Appointment-related
    if any(word in user_lower for word in ["appointment", "schedule", "book", "visit"]):
        return [
            {
                "id": "action_1",
                "label": "Provide Preferred Dates",
                "description": "Let me know your available times",
                "type": "schedule",
                "priority": "high",
                "icon": "Calendar"
            },
            {
                "id": "action_2",
                "label": "Share Contact Info",
                "description": "Give your phone number for confirmation",
                "type": "contact",
                "priority": "medium",
                "icon": "Phone"
            },
            {
                "id": "action_3",
                "label": "View Available Times",
                "description": "See all open appointment slots",
                "type": "view",
                "priority": "medium",
                "icon": "Eye"
            }
        ]
    
    # Pain/Emergency-related
    if any(word in user_lower for word in ["pain", "hurt", "emergency", "urgent", "swelling"]):
        return [
            {
                "id": "action_1",
                "label": "Book Emergency Appointment",
                "description": "Get examined by Dr. Smith today",
                "type": "schedule",
                "priority": "high",
                "icon": "Calendar"
            },
            {
                "id": "action_2",
                "label": "Contact Dr. Smith Directly",
                "description": "Urgent medical consultation",
                "type": "contact",
                "priority": "high",
                "icon": "Phone"
            },
            {
                "id": "action_3",
                "label": "View Pain Management Tips",
                "description": "Safe home remedies while you wait",
                "type": "view",
                "priority": "medium",
                "icon": "Eye"
            }
        ]
    
    # Billing/Payment-related
    if any(word in user_lower for word in ["cost", "price", "pay", "billing", "insurance", "invoice"]):
        return [
            {
                "id": "action_1",
                "label": "View Invoice Details",
                "description": "See itemized breakdown",
                "type": "financial",
                "priority": "medium",
                "icon": "DollarSign"
            },
            {
                "id": "action_2",
                "label": "Set Up Payment Plan",
                "description": "Flexible payment options",
                "type": "financial",
                "priority": "medium",
                "icon": "DollarSign"
            },
            {
                "id": "action_3",
                "label": "Contact Billing",
                "description": "Speak with our billing specialist",
                "type": "contact",
                "priority": "low",
                "icon": "Phone"
            }
        ]
    
    # General info/hours
    if any(word in user_lower for word in ["hours", "open", "closed", "location", "address"]):
        return [
            {
                "id": "action_1",
                "label": "Book Appointment",
                "description": "Schedule a visit during our hours",
                "type": "schedule",
                "priority": "medium",
                "icon": "Calendar"
            },
            {
                "id": "action_2",
                "label": "View Available Times",
                "description": "See all open slots",
                "type": "view",
                "priority": "medium",
                "icon": "Eye"
            },
            {
                "id": "action_3",
                "label": "Contact Clinic",
                "description": "Call or message us directly",
                "type": "contact",
                "priority": "low",
                "icon": "Phone"
            }
        ]
    
    # Default fallback actions
    return [
        {
            "id": "action_1",
            "label": "Book Appointment",
            "description": "Schedule a visit with us",
            "type": "schedule",
            "priority": "medium",
            "icon": "Calendar"
        },
        {
            "id": "action_2",
            "label": "Ask Another Question",
            "description": "I'm here to help!",
            "type": "action",
            "priority": "low",
            "icon": "Play"
        },
        {
            "id": "action_3",
            "label": "Contact Clinic",
            "description": "Speak with our team",
            "type": "contact",
            "priority": "low",
            "icon": "Phone"
        }
    ]
