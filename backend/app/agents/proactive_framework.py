"""
Proactive Suggestions Framework for All Agents

Unified system for agents to surface actionable suggestions to doctors.
Supports fine-tuning and learning from doctor decisions over time.

Reference: Phase 3+ - All agents proactive
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    """Complexity level for suggested actions."""
    LOW = "low"  # 🟢 Agent can guide
    MEDIUM = "medium"  # 🟡 Recommend expert consultation
    HIGH = "high"  # 🔴 Require expert consultation


class ActionCategory(str, Enum):
    """Category of suggested action."""
    # Alex (Reception)
    APPOINTMENT = "appointment"
    FOLLOWUP = "followup"
    REMINDER = "reminder"
    PATIENT_COMMUNICATION = "patient_communication"
    
    # Sarah (Clinical)
    TREATMENT = "treatment"
    DIAGNOSIS = "diagnosis"
    REFERRAL = "referral"
    PREVENTIVE_CARE = "preventive_care"
    
    # Marcus (CFO)
    TAX_OPTIMIZATION = "tax_optimization"
    FINANCIAL_PLANNING = "financial_planning"
    COST_REDUCTION = "cost_reduction"
    REVENUE_OPPORTUNITY = "revenue_opportunity"
    
    # Sophia (Operations)
    PROCESS_IMPROVEMENT = "process_improvement"
    INVENTORY = "inventory"
    STAFFING = "staffing"
    COMPLIANCE = "compliance"


class SuggestedAction(BaseModel):
    """A single suggested action from an agent."""
    
    # Core fields
    title: str  # Short title (e.g., "Schedule follow-up for Patient X")
    description: str  # Detailed description
    category: ActionCategory
    complexity: ComplexityLevel
    agent: str  # Which agent suggested this (alex, sarah, marcus, sophia)
    
    # Context
    reasoning: str  # Why this action is suggested
    data_points: Optional[List[str]] = None  # Supporting data
    
    # Execution
    can_auto_execute: bool = False  # Can agent execute without approval?
    requires_expert: bool = False  # Requires external expert (רו"ח, מומחה)?
    expert_type: Optional[str] = None  # Type of expert needed
    
    # Learning
    confidence: float = 0.5  # 0-1, will improve with fine-tuning
    similar_past_actions: int = 0  # How many similar actions in history
    
    # Optional execution details
    action_params: Optional[Dict[str, Any]] = None  # Parameters for execution


class ProactiveSuggestions(BaseModel):
    """Collection of suggestions from an agent."""
    
    agent: str
    suggestions: List[SuggestedAction]
    context: str  # Overall context for these suggestions
    timestamp: str


def format_suggestions_for_display(suggestions: ProactiveSuggestions) -> str:
    """
    Format suggestions for display to doctor.
    
    Args:
        suggestions: ProactiveSuggestions object
        
    Returns:
        Formatted string for display
    """
    if not suggestions.suggestions:
        return ""
    
    output = f"\n\n💡 **Suggested Actions from {suggestions.agent.title()}:**\n\n"
    
    # Group by complexity
    low = [s for s in suggestions.suggestions if s.complexity == ComplexityLevel.LOW]
    medium = [s for s in suggestions.suggestions if s.complexity == ComplexityLevel.MEDIUM]
    high = [s for s in suggestions.suggestions if s.complexity == ComplexityLevel.HIGH]
    
    # Format low complexity (green)
    if low:
        output += "**🟢 I can help you with these:**\n\n"
        for i, action in enumerate(low, 1):
            output += f"{i}. **{action.title}**\n"
            output += f"   {action.description}\n"
            if action.can_auto_execute:
                output += f"   ✅ I can do this for you - just say yes!\n"
            output += f"\n"
    
    # Format medium complexity (yellow)
    if medium:
        output += "**🟡 Recommended - Consider expert consultation:**\n\n"
        for i, action in enumerate(medium, 1):
            output += f"{i}. **{action.title}**\n"
            output += f"   {action.description}\n"
            if action.expert_type:
                output += f"   💡 Recommended: Consult with {action.expert_type}\n"
            output += f"   📊 I can prepare the data/analysis for you\n"
            output += f"\n"
    
    # Format high complexity (red)
    if high:
        output += "**🔴 Important - Expert consultation required:**\n\n"
        for i, action in enumerate(high, 1):
            output += f"{i}. **{action.title}**\n"
            output += f"   {action.description}\n"
            output += f"   ⚠️ REQUIRED: Must consult with {action.expert_type or 'expert'}\n"
            output += f"   📋 Reason: {action.reasoning}\n"
            output += f"\n"
    
    return output


def create_suggestion(
    agent: str,
    title: str,
    description: str,
    category: ActionCategory,
    complexity: ComplexityLevel,
    reasoning: str,
    can_auto_execute: bool = False,
    requires_expert: bool = False,
    expert_type: Optional[str] = None,
    data_points: Optional[List[str]] = None,
    confidence: float = 0.5,
) -> SuggestedAction:
    """
    Helper to create a suggestion.
    
    Args:
        agent: Agent name (alex, sarah, marcus, sophia)
        title: Short title
        description: Detailed description
        category: Action category
        complexity: Complexity level
        reasoning: Why this is suggested
        can_auto_execute: Can execute without approval
        requires_expert: Requires external expert
        expert_type: Type of expert (e.g., "רו\"ח", "אורתודונט")
        data_points: Supporting data
        confidence: Confidence level (0-1)
        
    Returns:
        SuggestedAction object
    """
    return SuggestedAction(
        agent=agent,
        title=title,
        description=description,
        category=category,
        complexity=complexity,
        reasoning=reasoning,
        can_auto_execute=can_auto_execute,
        requires_expert=requires_expert,
        expert_type=expert_type,
        data_points=data_points,
        confidence=confidence,
    )


# Example usage templates for each agent

ALEX_SUGGESTION_TEMPLATE = """
When analyzing patient interactions, identify:
- Patients who need follow-up appointments
- Patients who missed appointments
- Patients with upcoming birthdays
- Patients who haven't visited in 6+ months
- Opportunities to improve patient satisfaction

Format suggestions using create_suggestion() with:
- category: APPOINTMENT, FOLLOWUP, REMINDER, PATIENT_COMMUNICATION
- complexity: Usually LOW (you can handle most reception tasks)
- can_auto_execute: True for simple tasks (send reminder, schedule appointment)
"""

SARAH_SUGGESTION_TEMPLATE = """
When analyzing clinical data, identify:
- Patients needing follow-up treatments
- Incomplete treatment plans
- Preventive care opportunities (cleaning, checkup)
- Cases requiring specialist referral
- Potential complications or risks

Format suggestions using create_suggestion() with:
- category: TREATMENT, DIAGNOSIS, REFERRAL, PREVENTIVE_CARE
- complexity: 
  - LOW: Routine checkups, cleanings
  - MEDIUM: Complex treatments (consider specialist input)
  - HIGH: Serious conditions (require specialist)
- requires_expert: True for specialist referrals
- expert_type: Type of specialist needed
"""

MARCUS_SUGGESTION_TEMPLATE = """
When analyzing financial data, identify:
- Tax optimization opportunities
- Cost reduction possibilities
- Revenue growth opportunities
- Upcoming tax deadlines
- Financial risks or issues

Format suggestions using create_suggestion() with:
- category: TAX_OPTIMIZATION, FINANCIAL_PLANNING, COST_REDUCTION, REVENUE_OPPORTUNITY
- complexity:
  - LOW: Simple tracking, reminders
  - MEDIUM: Optimization strategies (recommend רו\"ח)
  - HIGH: Tax planning, legal matters (require רו\"ח)
- requires_expert: True for complex tax/legal matters
- expert_type: "רו\"ח" or "יועץ מס"
"""

SOPHIA_SUGGESTION_TEMPLATE = """
When analyzing operations data, identify:
- Process inefficiencies
- Inventory issues (low stock, expiring items)
- Staffing needs or scheduling conflicts
- Compliance requirements
- Equipment maintenance needs

Format suggestions using create_suggestion() with:
- category: PROCESS_IMPROVEMENT, INVENTORY, STAFFING, COMPLIANCE
- complexity:
  - LOW: Simple operational tasks
  - MEDIUM: Process changes (consider impact)
  - HIGH: Compliance, legal (require expert)
- can_auto_execute: True for inventory orders, scheduling
"""


__all__ = [
    'ComplexityLevel',
    'ActionCategory',
    'SuggestedAction',
    'ProactiveSuggestions',
    'format_suggestions_for_display',
    'create_suggestion',
    'ALEX_SUGGESTION_TEMPLATE',
    'SARAH_SUGGESTION_TEMPLATE',
    'MARCUS_SUGGESTION_TEMPLATE',
    'SOPHIA_SUGGESTION_TEMPLATE',
]

