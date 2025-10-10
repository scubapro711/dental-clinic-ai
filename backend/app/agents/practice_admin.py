import os
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
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            temperature=0.3,  # Lower temperature for consistent operations decisions
        )
        
        self.system_prompt = """You are Sophia, the Operations Manager Agent for a dental clinic.

Your role is to manage clinic operations, scheduling, workflow optimization, and inventory/supply management.

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

5. **Inventory & Supply Management**
   - Monitor stock levels
   - Track low stock alerts
   - Manage expiring products
   - Create purchase orders
   - Track inventory valuation
   - Suggest reorder quantities
   - Generate inventory reports

6. **Staff & HR Management**
   - Manage staff list and information
   - Track doctor availability
   - Create staff schedules
   - Monitor attendance
   - Handle time-off requests
   - Analyze staff workload
   - Track performance metrics
   - Balance workload distribution

7. **Compliance & Facilities Management** ⭐ NEW
   - Track treatment rooms and schedules
   - Manage equipment inventory
   - Handle maintenance requests
   - Monitor compliance deadlines
   - Create safety checklists
   - Track regulatory requirements
   - Generate compliance reports
   - Optimize room utilization

**Available Tools (38 total):**

**Scheduling Tools (8):**
- get_schedule_conflicts: Find scheduling conflicts
- get_available_slots: Find available appointment slots
- reschedule_appointment: Reschedule an appointment
- cancel_appointment: Cancel an appointment
- get_staff_schedule: View staff availability
- get_room_availability: Check room availability
- optimize_schedule: Optimize daily schedule
- get_operational_metrics: View operations KPIs

**Inventory Tools (10):**
- check_inventory_levels: Check current stock levels
- get_low_stock_alerts: Get low stock alerts
- track_expiring_products: Track products expiring soon
- create_purchase_order: Create purchase order for supplies
- get_purchase_orders: View recent purchase orders
- get_inventory_valuation: Get total inventory value
- get_stock_movements: Track stock in/out movements
- suggest_reorder_quantities: AI-powered reorder suggestions
- get_storage_locations: View storage locations
- generate_inventory_report: Generate comprehensive reports

**Staff Management Tools (10):**
- get_staff_list: View all clinic staff
- get_doctor_availability: Check doctor availability
- create_staff_schedule: Create schedule slots
- get_staff_attendance: Track attendance records
- get_time_off_requests: View time-off requests
- approve_time_off: Approve time-off requests
- get_staff_workload: Analyze staff workload
- get_staff_performance: Track performance metrics
- balance_staff_workload: Suggest workload balancing
- generate_staff_report: Generate HR reports

**Compliance & Facilities Tools (10):** ⭐ NEW
- get_rooms_list: View all treatment rooms
- get_room_schedule: Check room schedule
- get_equipment_list: View clinic equipment
- create_maintenance_request: Request equipment maintenance
- get_maintenance_requests: View maintenance requests
- get_compliance_reminders: Check compliance deadlines
- create_safety_checklist: Create safety checklists
- check_equipment_maintenance: Check maintenance schedule
- generate_compliance_report: Generate compliance reports
- optimize_room_utilization: Optimize room usage

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

═══════════════════════════════════════════════════════════════════
🎯  SUGGESTED ACTIONS (Phase 7: Agentic System)
═══════════════════════════════════════════════════════════════════

**IMPORTANT: YOU decide what operational actions to suggest based on analysis!**

After analyzing operational data, suggest specific actions to improve clinic operations.

**Format (REQUIRED):**

**Suggested Actions:**
1. [Action Name] - Brief description
2. [Action Name] - Brief description
3. [Action Name] - Brief description

**Guidelines:**
- Analyze operational data first
- Suggest 1-3 actions based on your analysis
- Be specific and actionable
- Prioritize by operational impact
- Consider both efficiency and patient experience

**Examples:**

**Scenario: Scheduling conflicts detected**
```
Found 3 double-bookings for tomorrow and 2 staff conflicts.

**Suggested Actions:**
1. [Resolve Double-Bookings] - Reschedule conflicting appointments
2. [Adjust Staff Schedule] - Coordinate coverage for conflicts
3. [Add Buffer Time] - Prevent future scheduling issues
```

**Scenario: High no-show rate**
```
No-show rate is 18% this month (clinic average: 8%).

**Suggested Actions:**
1. [Send Appointment Reminders] - Automated SMS 24h before
2. [Implement Confirmation System] - Require patient confirmation
3. [Review Cancellation Policy] - Consider deposit for new patients
```

**Scenario: Low clinic utilization**
```
Clinic utilization is 65% (target: 85%). Many empty slots.

**Suggested Actions:**
1. [Optimize Appointment Slots] - Adjust slot duration by treatment type
2. [Fill Empty Slots] - Contact waitlist patients
3. [Adjust Operating Hours] - Shift hours to match demand
```

**Scenario: Staff overload**
```
Dr. Smith has 12 appointments tomorrow (recommended max: 10).

**Suggested Actions:**
1. [Reschedule Non-Urgent] - Move 2 routine cleanings to next week
2. [Add Assistant Time] - Allocate extra assistant support
3. [Review Booking Rules] - Prevent future overbooking
```

**Scenario: Efficient operations**
```
Operations running smoothly! 92% utilization, 0 conflicts.

**Suggested Actions:**
1. [Maintain Current Schedule] - Keep current optimization
2. [Plan for Growth] - Prepare for additional capacity
3. [Staff Training] - Invest in efficiency improvements
```

**When NOT to suggest actions:**
- Simple schedule queries ("What's tomorrow's schedule?")
- Already resolved issues
- Casual conversation

**Remember:**
- YOU analyze operations and decide what to recommend
- Base suggestions on operational metrics
- Think: "What would an operations manager do?"
- Consider patient experience AND staff wellbeing

Always prioritize:
1. Patient care quality
2. Clinic efficiency
3. Staff satisfaction
4. Resource optimization

Respond in Hebrew or English based on the user's language."""

        logger.info("Practice Admin Agent initialized")
    
    def process(self, state: AgentState) -> AgentState:
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
            
            # Import scheduling tools
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
            
            # Import inventory tools
            from app.agents.tools.sophia_inventory_tools import (
                check_inventory_levels_tool,
                get_low_stock_alerts_tool,
                track_expiring_products_tool,
                create_purchase_order_tool,
                get_purchase_orders_tool,
                get_inventory_valuation_tool,
                get_stock_movements_tool,
                suggest_reorder_quantities_tool,
                get_storage_locations_tool,
                generate_inventory_report_tool,
            )
            
            # Import staff management tools
            from app.agents.tools.sophia_staff_tools import (
                get_staff_list_tool,
                get_doctor_availability_tool,
                create_staff_schedule_tool,
                get_staff_attendance_tool,
                get_time_off_requests_tool,
                approve_time_off_tool,
                get_staff_workload_tool,
                get_staff_performance_tool,
                balance_staff_workload_tool,
                generate_staff_report_tool,
            )
            
            # Import compliance & facilities tools
            from app.agents.tools.sophia_compliance_tools import (
                get_rooms_list_tool,
                get_room_schedule_tool,
                get_equipment_list_tool,
                create_maintenance_request_tool,
                get_maintenance_requests_tool,
                get_compliance_reminders_tool,
                create_safety_checklist_tool,
                check_equipment_maintenance_tool,
                generate_compliance_report_tool,
                optimize_room_utilization_tool,
            )
            
            # Import RAG tool for operational knowledge
            from app.agents.tools.rag_tools import search_operational_knowledge_tool
            
            # Bind all tools to LLM (39 tools total: 38 + RAG)
            llm_with_tools = self.llm.bind_tools([
                # Scheduling tools (8)
                get_schedule_conflicts_tool,
                get_available_slots_tool,
                reschedule_appointment_tool,
                cancel_appointment_tool,
                get_staff_schedule_tool,
                get_room_availability_tool,
                optimize_schedule_tool,
                get_operational_metrics_tool,
                # Inventory tools (10)
                check_inventory_levels_tool,
                get_low_stock_alerts_tool,
                track_expiring_products_tool,
                create_purchase_order_tool,
                get_purchase_orders_tool,
                get_inventory_valuation_tool,
                get_stock_movements_tool,
                suggest_reorder_quantities_tool,
                get_storage_locations_tool,
                generate_inventory_report_tool,
                # Staff management tools (10)
                get_staff_list_tool,
                get_doctor_availability_tool,
                create_staff_schedule_tool,
                get_staff_attendance_tool,
                get_time_off_requests_tool,
                approve_time_off_tool,
                get_staff_workload_tool,
                get_staff_performance_tool,
                balance_staff_workload_tool,
                generate_staff_report_tool,
                # Compliance & facilities tools (10)
                get_rooms_list_tool,
                get_room_schedule_tool,
                get_equipment_list_tool,
                create_maintenance_request_tool,
                get_maintenance_requests_tool,
                get_compliance_reminders_tool,
                create_safety_checklist_tool,
                check_equipment_maintenance_tool,
                generate_compliance_report_tool,
                optimize_room_utilization_tool,
                # RAG tool (1)
                search_operational_knowledge_tool,  # Safety protocols, compliance
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
                    if tool_name == "get_schedule_conflicts_tool":
                        result = get_schedule_conflicts_tool.invoke(tool_args)
                    elif tool_name == "get_available_slots_tool":
                        result = get_available_slots_tool.invoke(tool_args)
                    elif tool_name == "reschedule_appointment_tool":
                        result = reschedule_appointment_tool.invoke(tool_args)
                    elif tool_name == "cancel_appointment_tool":
                        result = cancel_appointment_tool.invoke(tool_args)
                    elif tool_name == "get_staff_schedule_tool":
                        result = get_staff_schedule_tool.invoke(tool_args)
                    elif tool_name == "get_room_availability_tool":
                        result = get_room_availability_tool.invoke(tool_args)
                    elif tool_name == "optimize_schedule_tool":
                        result = optimize_schedule_tool.invoke(tool_args)
                    elif tool_name == "get_operational_metrics_tool":
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
            
            # Parse suggested actions from response (Phase 7: Agentic System)
            from app.agents.utils.action_parser import parse_suggested_actions
            suggested_actions = parse_suggested_actions(response_text)
            
            if suggested_actions:
                logger.info(f"Practice Admin suggested {len(suggested_actions)} actions")
            
            # Add response to messages
            state["messages"].append(AIMessage(content=response_text))
            
            # Add suggested actions to state
            state["suggested_actions"] = suggested_actions if suggested_actions else None
            
            logger.info("Practice Admin completed operations analysis")
            
            return state
            
        except Exception as e:
            logger.error(f"Practice Admin error: {e}")
            error_message = f"I encountered an error while processing your operations request: {str(e)}"
            state["messages"].append(AIMessage(content=error_message))
            return state
