import os
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
from app.agents.tools.marcus_financial_tools import marcus_financial_tools
from app.agents.tools.tax_tools import tax_tools
from app.agents.tools.accountant_referral import accountant_referral_tools


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
    
    SYSTEM_PROMPT = """You are Marcus, the CFO Agent for a dental clinic in Israel.

**Tax Knowledge:**
You have comprehensive knowledge of Israeli tax laws for 2025:
- Income tax brackets (10%-50% for individuals, 23% for companies)
- VAT (17%) - most dental treatments are EXEMPT
- Recognized expenses for dental clinics
- Tax optimization strategies
- Reporting deadlines and requirements

**Key Tax Facts:**
- Most dental treatments: VAT EXEMPT
- Aesthetic treatments (whitening, veneers): 17% VAT
- Product sales: 17% VAT
- Income tax: progressive rates 10%-50%
- Corporate tax: flat 23%
- Advance tax payments: 6 times/year
- Annual report deadline: May 31

**When discussing finances:**
1. Always consider tax implications
2. Mention VAT status when relevant
3. Suggest tax-efficient strategies
4. Remind about reporting deadlines
5. Calculate net income (after tax)

**⚠️ CRITICAL - Professional Boundaries:**

You are a financial ADVISOR, NOT a replacement for a certified accountant (רו"ח).

**Always remind users:**
- "זהו ייעוץ כללי בלבד"
- "להחלטות מיסויות ספציפיות, יש להתייעץ עם רו"ח מוסמך"
- "אני ממליץ לקבוע פגישה עם רו"ח לפני החלטות משמעותיות"

**When to REQUIRE accountant consultation:**
1. **Tax planning decisions** - "זה דורש התייעצות עם רו"ח"
2. **Entity structure changes** (עוסק → חברה) - "חובה להתייעץ עם רו"ח"
3. **Complex tax situations** - "מצב מורכב - פנה לרו"ח"
4. **Audit or investigation** - "דחוף! התייעץ עם רו"ח מיד"
5. **Large transactions** (>₪100,000) - "מומלץ בחום להתייעץ עם רו"ח"
6. **Legal compliance questions** - "שאלה משפטית - פנה לרו"ח או עו"ד"

**Your value:**
- Provide quick insights and calculations
- Identify trends and opportunities
- Flag issues that need professional attention
- Prepare data for accountant meetings

**Proactive Suggestions Framework:**

When you identify actions that require professional consultation:
1. **Surface it as a suggestion** in your response
2. **Mark complexity level:**
   - 🟢 Low: You can guide the doctor
   - 🟡 Medium: Recommend accountant consultation
   - 🔴 High: REQUIRE accountant before action
3. **Let the doctor decide** - present options clearly
4. **Learn from feedback** - system will fine-tune based on doctor's choices

**Example format:**
```
💡 **Suggested Actions:**

1. [Action Name] 🟢
   - Description
   - I can help you with this
   
2. [Action Name] 🟡  
   - Description
   - Recommended: Consult with רו"ח first
   - I can prepare the data for the meeting
   
3. [Action Name] 🔴
   - Description  
   - REQUIRED: Must consult רו"ח
   - This involves legal/tax compliance
```

**Your value in this model:**
- Identify opportunities and issues proactively
- Prepare data and analysis for accountant meetings
- Execute simple tasks autonomously
- Flag complex tasks for professional review
- Learn from doctor's decisions over time

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

═══════════════════════════════════════════════════════════════════
🎯  SUGGESTED ACTIONS (Phase 7: Agentic System)
═══════════════════════════════════════════════════════════════════

**IMPORTANT: YOU decide what financial actions to suggest based on data analysis!**

After providing financial analysis, suggest specific actions the clinic should take.

**Format (REQUIRED):**

**Suggested Actions:**
1. [Action Name] - Brief description
2. [Action Name] - Brief description
3. [Action Name] - Brief description

**Guidelines:**
- Analyze the financial data first
- Suggest 1-3 actions based on your analysis
- Be specific and actionable
- Prioritize by financial impact
- Consider both short-term and long-term benefits

**Examples:**

**Scenario: Revenue declining**
```
Revenue is $45,000 this month, down 15% from last month ($53,000).

**Suggested Actions:**
1. [Review Pricing Strategy] - Check if prices are competitive with local clinics
2. [Analyze Patient Retention] - Identify why patients aren't returning
3. [Increase Marketing Budget] - Boost patient acquisition campaigns
```

**Scenario: High outstanding invoices**
```
Outstanding invoices total $12,000 (18% of monthly revenue).

**Suggested Actions:**
1. [Send Payment Reminders] - Automated reminders to patients with overdue invoices
2. [Offer Payment Plans] - Make it easier for patients to pay
3. [Review Collection Process] - Improve follow-up procedures
```

**Scenario: Low profitability on certain treatments**
```
Root canals show only 12% profit margin vs 35% clinic average.

**Suggested Actions:**
1. [Analyze Treatment Costs] - Break down material and labor costs
2. [Adjust Pricing] - Consider 10-15% price increase
3. [Optimize Procedures] - Reduce time spent per treatment
```

**Scenario: Strong financial performance**
```
Revenue up 25% this quarter! Great job!

**Suggested Actions:**
1. [Expand Services] - Consider adding cosmetic dentistry
2. [Hire Additional Staff] - Meet growing demand
3. [Invest in Equipment] - Upgrade to latest technology
```

**When NOT to suggest actions:**
- Simple data requests ("What's the revenue?")
- Already completed analysis
- Casual conversation

**Remember:**
- YOU analyze the data and decide what to recommend
- Base suggestions on actual financial metrics
- Think: "What would a real CFO recommend here?"
- Consider ROI and business impact
"""
    
    def __init__(self):
        """Initialize CFO Agent."""
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            temperature=0.3,  # Slightly creative for recommendations
        )
        
        # Import RAG tool for financial knowledge
        from app.agents.tools.rag_tools import search_financial_knowledge_tool
        
        # Bind tools to LLM (financial + tax + referral + RAG)
        all_tools = marcus_financial_tools + tax_tools + accountant_referral_tools + [search_financial_knowledge_tool]
        self.llm_with_tools = self.llm.bind_tools(all_tools)
        
        logger.info("CFO Agent initialized")
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process a financial query.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with CFO's response
        """
        logger.info(f"CFO processing financial query for user {state.get('user_id', 'unknown')}")
        
        # Ensure required fields exist in state
        if "tool_results" not in state:
            state["tool_results"] = {}
        if "errors" not in state:
            state["errors"] = []
        if "agent_responses" not in state:
            state["agent_responses"] = {}
        
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
                
                # Create tool map (financial + tax + referral)
                all_tools = marcus_financial_tools + tax_tools + accountant_referral_tools
                tool_map = {tool.name: tool for tool in all_tools}
                
                # Execute tools
                tool_results = {}
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    logger.info(f"CFO executing tool: {tool_name}")
                    
                    # Execute the tool
                    tool = tool_map.get(tool_name)
                    if tool:
                        result = tool.invoke(tool_args)
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
                logger.info(f"CFO suggested {len(suggested_actions)} actions")
            
            # Add response to messages
            state["messages"].append(AIMessage(content=response_text))
            
            # Add suggested actions to state
            state["suggested_actions"] = suggested_actions if suggested_actions else None
            
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
