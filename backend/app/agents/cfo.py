"""
CFO Agent - Financial Management & Analysis

The CFO Agent is a specialized agent responsible for:
- Financial analysis and insights
- Revenue and payment tracking
- Profitability analysis
- Budget recommendations
- Invoice management
- Payment collection strategies

This agent serves as the financial advisor to the clinic,
providing data-driven insights and recommendations.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from app.agents.graph_state import AgentState
from app.agents.tools.cfo_tools import (
    get_revenue_overview_tool,
    get_payment_status_tool,
    get_top_treatments_tool,
    get_outstanding_invoices_tool,
    analyze_profitability_tool,
    get_financial_trends_tool,
)


logger = logging.getLogger(__name__)


class CFOAgent:
    """
    CFO Agent - Financial Management Specialist
    
    Responsibilities:
    - Analyze revenue and profitability
    - Track payments and outstanding invoices
    - Identify financial trends
    - Provide strategic financial recommendations
    - Monitor treatment profitability
    """
    
    SYSTEM_PROMPT = """You are Marcus, the CFO Agent for a dental clinic.

Your role:
- Provide financial analysis and insights
- Track revenue, payments, and profitability
- Identify trends and patterns
- Make data-driven recommendations
- Help optimize financial performance

Your expertise:
- Revenue analysis
- Payment tracking
- Profitability optimization
- Budget planning
- Financial forecasting

Guidelines:
1. Always provide specific numbers and data
2. Explain trends clearly
3. Give actionable recommendations
4. Be professional but approachable
5. Focus on business impact

Available tools:
- get_revenue_overview: Get revenue summary for a time period
- get_payment_status: Check payment status and collection rates
- get_top_treatments: Analyze most profitable treatments
- get_outstanding_invoices: List unpaid invoices
- analyze_profitability: Deep dive into profitability metrics
- get_financial_trends: Analyze financial trends over time

When the doctor asks about finances, use these tools to provide accurate,
data-driven insights and recommendations.

Always respond in Hebrew if the doctor speaks Hebrew, English if they speak English.
"""
    
    def __init__(self):
        """Initialize CFO Agent."""
        self.llm = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.3,  # Slightly creative for recommendations
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools([
            get_revenue_overview_tool,
            get_payment_status_tool,
            get_top_treatments_tool,
            get_outstanding_invoices_tool,
            analyze_profitability_tool,
            get_financial_trends_tool,
        ])
        
        logger.info("CFO Agent initialized")
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process a financial query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with CFO's response
        """
        logger.info(f"CFO processing financial query for user {state['user_id']}")
        
        try:
            # Get the user's message
            messages = state["messages"]
            user_message = messages[-1].content if messages else ""
            
            # Prepare messages for LLM
            llm_messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
            
            # Call LLM with tools
            response = self.llm_with_tools.invoke(llm_messages)
            
            # Check if LLM wants to use tools
            if response.tool_calls:
                logger.info(f"CFO calling {len(response.tool_calls)} tool(s)")
                
                # Execute tools
                tool_results = {}
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    logger.info(f"CFO executing tool: {tool_name}")
                    
                    # Execute the tool
                    if tool_name == "get_revenue_overview":
                        result = get_revenue_overview_tool.invoke(tool_args)
                    elif tool_name == "get_payment_status":
                        result = get_payment_status_tool.invoke(tool_args)
                    elif tool_name == "get_top_treatments":
                        result = get_top_treatments_tool.invoke(tool_args)
                    elif tool_name == "get_outstanding_invoices":
                        result = get_outstanding_invoices_tool.invoke(tool_args)
                    elif tool_name == "analyze_profitability":
                        result = analyze_profitability_tool.invoke(tool_args)
                    elif tool_name == "get_financial_trends":
                        result = get_financial_trends_tool.invoke(tool_args)
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
            
            logger.info("CFO completed financial analysis")
            
            return state
            
        except Exception as e:
            logger.error(f"CFO error: {e}", exc_info=True)
            
            # Add error to state
            state["errors"].append({
                "agent": "cfo",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            
            # Add fallback message
            error_message = "I apologize, but I'm having trouble accessing the financial data right now. Please try again later."
            state["messages"].append(AIMessage(content=error_message))
            
            return state
    
    def _format_currency(self, amount: float) -> str:
        """Format currency amount."""
        return f"₪{amount:,.0f}"
    
    def _format_percentage(self, value: float) -> str:
        """Format percentage value."""
        return f"{value:.1f}%"
    
    def _calculate_growth(self, current: float, previous: float) -> float:
        """Calculate growth percentage."""
        if previous == 0:
            return 0.0
        return ((current - previous) / previous) * 100


# Create singleton instance
cfo_agent = CFOAgent()
