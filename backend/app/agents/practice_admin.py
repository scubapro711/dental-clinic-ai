"""
Practice Admin Agent - Operations & Scheduling Management

This agent handles:
- Appointment scheduling and conflicts
- Clinic operations management
- Staff coordination
- Resource allocation
- Workflow optimization
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.agents.graph_state import AgentState

logger = logging.getLogger(__name__)


class PracticeAdminAgent:
    """
    Practice Administrator Agent for clinic operations management.
    
    Responsibilities:
    - Appointment scheduling and rescheduling
    - Conflict resolution (double bookings, cancellations)
    - Staff coordination
    - Resource allocation (rooms, equipment)
    - Workflow optimization
    - Operational analytics
    """
    
    def __init__(self):
        """Initialize Practice Admin Agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.3,  # Lower temperature for consistent operations decisions
        )
        
        self.system_prompt = """You are Sophia, the Practice Administrator Agent for a dental clinic.

Your role is to manage clinic operations, scheduling, and workflow optimization.

**Core Responsibilities:**
1. **Appointment Management**
   - Schedule new appointments
   - Handle rescheduling requests
   - Resolve scheduling conflicts
   - Optimize appointment slots

2. **Conflict Resolution**
   - Double bookings
   - Cancellations and no-shows
   - Staff availability conflicts
   - Resource allocation issues

3. **Operations Optimization**
   - Maximize clinic utilization
   - Minimize wait times
   - Balance doctor workload
   - Optimize room usage

4. **Staff Coordination**
   - Track staff schedules
   - Coordinate breaks and shifts
   - Handle emergency coverage

**Available Tools:**
- get_schedule_conflicts: Find scheduling conflicts
- get_available_slots: Find available appointment slots
- reschedule_appointment: Reschedule an appointment
- get_staff_schedule: View staff availability
- get_room_availability: Check room availability
- optimize_schedule: Optimize daily schedule
- get_operational_metrics: View operations KPIs

**Communication Style:**
- Professional and efficient
- Clear and actionable recommendations
- Proactive problem-solving
- Data-driven decisions

**Decision Framework:**
1. Identify the operational issue
2. Analyze available options
3. Consider impact on patients and staff
4. Recommend optimal solution
5. Implement if authorized

**Escalation Rules:**
- Escalate to doctor for:
  - Medical priority decisions
  - Policy exceptions
  - Major schedule changes
  - Patient complaints

Always prioritize:
1. Patient care quality
2. Clinic efficiency
3. Staff satisfaction
4. Resource optimization

Respond in Hebrew or English based on the user's language."""

        logger.info("Practice Admin Agent initialized")
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Process operations/scheduling request.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with admin response
        """
        try:
            logger.info("Practice Admin processing operations request")
            
            # Get conversation history
            messages = state["messages"]
            
            # Import tools
            from app.agents.tools.admin_tools import (
                get_schedule_conflicts_tool,
                get_available_slots_tool,
                reschedule_appointment_tool,
                cancel_appointment_tool,
                get_staff_schedule_tool,
                get_room_availability_tool,
                optimize_schedule_tool,
                get_operational_metrics_tool,
            )
            
            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools([
                get_schedule_conflicts_tool,
                get_available_slots_tool,
                reschedule_appointment_tool,
                cancel_appointment_tool,
                get_staff_schedule_tool,
                get_room_availability_tool,
                optimize_schedule_tool,
                get_operational_metrics_tool,
            ])
            
            # Prepare messages for LLM
            llm_messages = [
                SystemMessage(content=self.system_prompt),
                *messages
            ]
            
            # Get LLM response
            response = llm_with_tools.invoke(llm_messages)
            
            # Check if tools were called
            if response.tool_calls:
                logger.info(f"Practice Admin calling {len(response.tool_calls)} tools")
                
                # Execute tools
                tool_results = {}
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("args", {})
                    
                    logger.info(f"Executing tool: {tool_name}")
                    
                    # Execute the tool
                    if tool_name == "get_schedule_conflicts":
                        result = get_schedule_conflicts_tool.invoke(tool_args)
                    elif tool_name == "get_available_slots":
                        result = get_available_slots_tool.invoke(tool_args)
                    elif tool_name == "reschedule_appointment":
                        result = reschedule_appointment_tool.invoke(tool_args)
                    elif tool_name == "get_staff_schedule":
                        result = get_staff_schedule_tool.invoke(tool_args)
                    elif tool_name == "get_room_availability":
                        result = get_room_availability_tool.invoke(tool_args)
                    elif tool_name == "optimize_schedule":
                        result = optimize_schedule_tool.invoke(tool_args)
                    elif tool_name == "get_operational_metrics":
                        result = get_operational_metrics_tool.invoke(tool_args)
                    else:
                        result = f"Unknown tool: {tool_name}"
                    
                    tool_results[tool_name] = result
                
                # Store tool results in state
                state["tool_results"].update(tool_results)
                
                # Generate final response with tool results
                from langchain_core.messages import ToolMessage
                
                tool_messages = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    result = tool_results.get(tool_name, "No result")
                    tool_messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_call["id"]
                        )
                    )
                
                final_messages = llm_messages + [response] + tool_messages
                
                final_response = self.llm.invoke(final_messages)
                response_text = final_response.content
            else:
                # No tools needed, use direct response
                response_text = response.content
            
            # Add response to messages
            state["messages"].append(AIMessage(content=response_text))
            
            logger.info("Practice Admin completed operations analysis")
            
            return state
            
        except Exception as e:
            logger.error(f"Practice Admin error: {e}")
            error_message = f"I encountered an error while processing your operations request: {str(e)}"
            state["messages"].append(AIMessage(content=error_message))
            return state
