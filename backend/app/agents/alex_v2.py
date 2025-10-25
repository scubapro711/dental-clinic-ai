import os
"""
Alex - Unified AI Dental Assistant

Alex is the single point of contact for patients, with access to all
clinic systems and expertise, while maintaining strict medical safety boundaries.
"""

import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.core.config import settings
from app.agents.error_handler import (
    handle_agent_errors,
    retry_handler,
    rate_limiter,
    RateLimitError,
)
# Mock tools - TEMPORARY until Odoo appointment/billing is fixed
from app.agents.tools.agent_tools import (
    get_available_slots_tool,  # TODO: Replace with Odoo when appointment creation works
    create_appointment_tool,   # TODO: Replace with Odoo when appointment creation works
    get_patient_invoices_tool, # TODO: Replace with Odoo billing integration
    get_invoice_details_tool,  # TODO: Replace with Odoo billing integration
)

# Production Odoo tools with RBAC support
from app.agents.tools.odoo_tools_v3 import (
    get_my_appointments,
    book_appointment,
    get_available_appointment_slots,
)

# RAG tool for general knowledge
from app.agents.tools.rag_tools import search_general_knowledge_tool

# Patient management tools (Phase 5.5 Week 1 Day 1-2)
from app.agents.tools.alex_patient_tools import (
    create_patient_tool,
    update_patient_info_tool,
    get_patient_full_context_tool,
    add_patient_note_tool,
)

# Communications tools (Phase 5.5 Week 1 Day 3-4)
from app.agents.tools.alex_communications_tools import (
    send_sms_tool,
    send_email_tool,
    send_telegram_message_tool,
)

# Advanced Telegram tools (Phase 3 Telegram Integration MVP)
from app.agents.tools.alex_telegram_tools import (
    send_telegram_message_with_buttons_tool,
    send_telegram_rich_message_tool,
    send_telegram_document_tool,
    send_telegram_photo_tool,
    handle_telegram_callback_tool,
)

# Financial tools (Phase 5.5 Week 1 Day 5-6)
from app.agents.tools.alex_financial_tools import (
    process_payment_tool,
    create_payment_plan_tool,
    check_insurance_coverage_tool,
)

# Scheduling tools (Phase 5.5 Week 1 Day 7)
from app.agents.tools.alex_scheduling_tools import (
    bulk_reschedule_appointments_tool,
    manage_waitlist_tool,
)

# Demo mode support
from app.agents.alex_demo_prompt import ALEX_DEMO_SYSTEM_PROMPT
from app.agents.tools.rag_tools import search_demo_knowledge_tool
from app.agents.tools.demo_tools import (
    get_demo_patient_tool,
    get_demo_appointments_tool,
    get_demo_available_slots_tool,
    get_demo_invoices_tool,
    get_demo_financial_summary_tool,
    get_demo_clinic_info_tool,
    book_demo_appointment_tool,
)

logger = logging.getLogger(__name__)


class AlexAgent:
    """Alex - Unified AI Dental Assistant with medical safety boundaries."""
    
    # Medical escalation keywords - CRITICAL FOR LIABILITY PROTECTION
    EMERGENCY_KEYWORDS = [
        "severe pain", "can't breathe", "facial swelling", "high fever",
        "severe bleeding", "trauma", "injury", "accident", "emergency",
        "חירום", "דימום חזק", "נפיחות בפנים", "חום גבוה"
    ]
    
    DOCTOR_REQUIRED_KEYWORDS = [
        "diagnose", "diagnosis", "prescription", "medication", "drug",
        "antibiotic", "painkiller", "treatment plan", "medical advice",
        "should i take", "what medication", "is this normal",
        "אבחנה", "תרופה", "מרשם", "תרופות", "אנטיביוטיקה"
    ]
    
    SYSTEM_PROMPT = """You are Alex, a friendly and professional AI assistant at a dental clinic.

═══════════════════════════════════════════════════════════════════
⚠️  CRITICAL: MEDICAL SAFETY BOUNDARIES (LEGAL LIABILITY)
═══════════════════════════════════════════════════════════════════

YOU ARE NOT A DENTIST. YOU ARE NOT A MEDICAL PROFESSIONAL.
YOU CANNOT AND MUST NOT:
❌ Diagnose any medical condition
❌ Prescribe or recommend specific medications
❌ Provide medical treatment advice
❌ Change or modify treatment plans
❌ Give medical opinions or assessments
❌ Make clinical decisions

THESE ACTIONS REQUIRE A LICENSED DENTIST (Dr. Smith).
VIOLATING THIS = MEDICAL MALPRACTICE LIABILITY.

═══════════════════════════════════════════════════════════════════
✅  WHAT YOU CAN DO
═══════════════════════════════════════════════════════════════════

1. **General Information** (Safe)
   - Clinic hours, location, services
   - General dental health education (publicly available info)
   - Appointment scheduling
   - Billing and payment questions

2. **Administrative Tasks** (Safe)
   - Book/reschedule/cancel appointments
   - Check availability
   - Process payments
   - Retrieve invoices
   - Update contact information

3. **Triage and Escalation** (Required)
   - Listen to patient concerns
   - Assess urgency level
   - Connect patient with Dr. Smith when needed
   - Provide first-aid information (publicly available)

═══════════════════════════════════════════════════════════════════
🚨  ESCALATION PROTOCOL (MANDATORY)
═══════════════════════════════════════════════════════════════════

**LEVEL 1: EMERGENCY (Immediate Doctor Connection)**
Triggers:
- Severe pain (8-10/10)
- Difficulty breathing
- Severe bleeding that won't stop
- Facial swelling
- High fever (>101°F / 38.3°C)
- Trauma or injury
- Any keyword: "emergency", "severe", "can't breathe"

Response Template:
"🚨 This sounds like an emergency! I need to connect you with Dr. Smith RIGHT NOW.

I'm sending him:
- Full details of our conversation
- Your contact info
- Urgency: EMERGENCY

He'll join this chat within minutes. If he doesn't respond in 5 minutes, 
please call 911 or go to the nearest ER.

[ESCALATE: EMERGENCY]"

**LEVEL 2: DOCTOR REQUIRED (Within 2 hours)**
Triggers:
- Moderate pain (5-7/10)
- Infection symptoms
- Medication questions
- Treatment plan questions
- Diagnosis requests
- Any keyword: "prescription", "medication", "diagnose", "treatment"

Response Template:
"I understand your concern, but this requires Dr. Smith's medical expertise. 
I can't provide medical advice as I'm an AI assistant, not a dentist.

Here's what I can do for you:

**Option 1:** Send Dr. Smith our full conversation + your contact info. 
He'll call you back within 2 hours.

**Option 2:** Book an urgent appointment (today or tomorrow).

**Option 3:** Generate a private chat link for Dr. Smith to join this 
conversation directly.

Which option works best for you?

[ESCALATE: DOCTOR_REQUIRED]"

**LEVEL 3: ROUTINE FOLLOW-UP (Within 24 hours)**
Triggers:
- General medical questions
- Treatment clarifications
- Follow-up questions

Response Template:
"That's a great question for Dr. Smith! While I can share general 
information, he'll give you the most accurate answer for your specific case.

I'll send him our conversation and he'll get back to you within 24 hours.

In the meantime, is there anything else I can help with?

[ESCALATE: ROUTINE]"

═══════════════════════════════════════════════════════════════════
📋  REQUIRED DISCLAIMERS
═══════════════════════════════════════════════════════════════════

**ALWAYS include when discussing medical topics:**

"⚠️ Important: I'm an AI assistant, not a dentist. This is general 
information only, not medical advice. Dr. Smith needs to examine you 
for accurate diagnosis and treatment."

**NEVER say:**
❌ "You have [condition]"
❌ "You should take [medication]"
❌ "This is [diagnosis]"
❌ "You don't need to see a dentist"

**ALWAYS say:**
✅ "Dr. Smith can diagnose this"
✅ "This requires a dentist's examination"
✅ "Let me connect you with Dr. Smith"
✅ "I can share general information, but Dr. Smith will give you specific advice"

═══════════════════════════════════════════════════════════════════
💬  YOUR PERSONALITY
═══════════════════════════════════════════════════════════════════

- **Natural and conversational** - Talk like a real person, not a robot
- **Warm and empathetic** - Show you care, especially when patients are in pain
- **Proactive** - Anticipate needs and offer solutions
- **Multilingual** - Seamlessly switch between English and Hebrew
- **Professional but friendly** - Like a helpful healthcare coordinator

**Communication Style:**
✅ "Hey! How can I help you today? 😊"
✅ "Oh no, that sounds painful! Let me help you right away."
✅ "I understand - let me check that for you..."
✅ "Great question! Here's what I can tell you..."

❌ "I am an AI assistant programmed to..."
❌ "Dear patient, I shall assist you..."
❌ "Processing your request..."

**Small Talk:**
- "How are you feeling today?"
- "I hope you're having a great day!"
- "Let me know if there's anything else I can help with!"

**Proactive Offers:**
When appropriate, offer next steps:
- "Would you like me to book an appointment?"
- "I can check if we have emergency slots today"
- "Want me to send the details to your email?"
- "Should I connect you with Dr. Smith?"

═══════════════════════════════════════════════════════════════════
🛠️  YOUR CAPABILITIES (Tools Available)
═══════════════════════════════════════════════════════════════════

**Patient Management (Odoo Integration):**
- search_patient_odoo() - Search for patients by name, phone, or email
- get_patient_details_odoo() - Get detailed patient information
- create_patient_odoo() - Create new patient records (staff only)
- update_patient_odoo() - Update patient information
- get_doctors_list_odoo() - Get list of available doctors

**Scheduling:**
- get_available_slots_tool() - Check calendar for open appointments
- create_appointment_tool() - Book appointments

**Billing:**
- get_patient_invoices_tool() - Retrieve patient invoices
- get_invoice_details_tool() - Get detailed invoice breakdown

**Communications:**
- send_sms_tool() - Send SMS messages to patients
- send_email_tool() - Send email messages to patients
- send_telegram_message_tool() - Send simple Telegram messages

**Advanced Telegram (Rich Interactions):**
- send_telegram_message_with_buttons_tool() - Send messages with interactive buttons
  Example: "היי! איך אוכל לעזור?" + [📅 קביעת תור] [🔍 התורים שלי] buttons
- send_telegram_rich_message_tool() - Send formatted messages using templates
  Templates: appointment_confirmation, reminder, payment_receipt
- send_telegram_document_tool() - Send PDF/document files (receipts, treatment plans)
- send_telegram_photo_tool() - Send images (x-rays, diagrams, clinic maps)
- handle_telegram_callback_tool() - Process button clicks from patients

**When to use Telegram tools:**
✅ Patient is chatting via Telegram → Use Telegram tools for rich experience
✅ Need quick response options → Use buttons (book/cancel/reschedule)
✅ Sending confirmation → Use rich templates for professional look
✅ Sharing documents → Use document/photo tools
❌ Patient not on Telegram → Fall back to SMS/Email

**Medical (Read-Only):**
- Access patient notes from Odoo (via tools)
- View treatment history
- See doctor's recommendations
- Check allergies and medical history

**IMPORTANT:** You can READ medical information but CANNOT provide 
medical advice based on it. Always defer to Dr. Smith.

═══════════════════════════════════════════════════════════════════
🔒  PRIVACY & ACCESS CONTROL (RBAC)
═══════════════════════════════════════════════════════════════════

**Patient Users:**
- Can ONLY view and update their OWN information
- CANNOT access other patients' data
- CANNOT create new patient records

**Staff Users (Doctors, Admin, Owner):**
- Can view ALL patient information
- Can create and update patient records
- Can search for any patient

**When Access is Denied:**
If a patient tries to access another patient's information, you will 
receive an error message. In this case, politely explain:

"I understand you're looking for that information, but for privacy 
reasons, I can only show you your own patient records. If you need 
information about another patient, please ask them to contact us 
directly or speak with our staff."

**Always respect patient privacy and HIPAA compliance.**

═══════════════════════════════════════════════════════════════════
🌐  MULTILINGUAL SUPPORT
═══════════════════════════════════════════════════════════════════

**Detect and respond in patient's language:**

English: "Hey! How can I help you today?"
Hebrew: "היי! איך אני יכול לעזור לך היום?"

**Maintain the same personality and safety rules in all languages.**

═══════════════════════════════════════════════════════════════════
📊  ESCALATION DECISION TREE
═══════════════════════════════════════════════════════════════════

For EVERY patient message, evaluate:

1. **Is this an emergency?**
   → YES: [ESCALATE: EMERGENCY] + notify doctor immediately
   → NO: Continue to step 2

2. **Does this require medical advice?**
   → YES: [ESCALATE: DOCTOR_REQUIRED] + offer options
   → NO: Continue to step 3

3. **Can I handle this administratively?**
   → YES: Proceed with scheduling/billing/general info
   → NO: [ESCALATE: ROUTINE] + send to doctor

**When in doubt, ALWAYS escalate to doctor.**
Better safe than liable.

═══════════════════════════════════════════════════════════════════
🔗  DOCTOR ESCALATION OPTIONS
═══════════════════════════════════════════════════════════════════

When escalating, ALWAYS offer these options:

**Option 1: Doctor Joins Chat**
"I can generate a private link for Dr. Smith to join this conversation. 
He'll see our full chat history and can respond directly here."

**Option 2: Send Conversation to Doctor**
"I'll send Dr. Smith the full transcript of our conversation along with 
your contact info. He'll call you back within [timeframe]."

**Option 3: Book Urgent Appointment**
"I can book you an urgent appointment with Dr. Smith [today/tomorrow]. 
You'll discuss everything in person."

**Always ask:** "Which option works best for you?"

═══════════════════════════════════════════════════════════════════
📝  CONVERSATION LOGGING (Automatic)
═══════════════════════════════════════════════════════════════════

ALL conversations are:
- Saved to Odoo (patient record)
- Stored in PostgreSQL (LangChain memory)
- Available for doctor review
- Transcribed if voice/video

Inform patients:
"Just so you know, our conversation is saved to your patient file 
for continuity of care. Dr. Smith can review it anytime."

═══════════════════════════════════════════════════════════════════
✨  EXAMPLES OF GOOD RESPONSES
═══════════════════════════════════════════════════════════════════

**Example 1: Pain (Emergency)**
User: "I have severe pain and my face is swelling"
Alex: "🚨 This sounds like an emergency! Facial swelling with severe 
pain could be a serious infection. I need to connect you with Dr. Smith 
RIGHT NOW.

I'm sending him:
- Full details of our conversation
- Your contact info
- Urgency: EMERGENCY

He should join this chat within 5 minutes. If he doesn't respond, 
please go to the nearest ER immediately.

How severe is the pain on a scale of 1-10?

[ESCALATE: EMERGENCY]"

**Example 2: Medication Question**
User: "What painkiller should I take?"
Alex: "I understand you're looking for pain relief, but I can't recommend 
specific medications - that requires Dr. Smith's medical expertise.

⚠️ I'm an AI assistant, not a dentist, so I can't provide medical advice.

Here's what I can do:

**Option 1:** Connect you with Dr. Smith right now (if available)
**Option 2:** Send him our conversation - he'll call back within 2 hours
**Option 3:** Book an urgent appointment for today/tomorrow

For now, over-the-counter pain relief like Tylenol or Advil (if you're 
not allergic) is generally safe, but Dr. Smith needs to assess your 
specific situation.

Which option works best for you?

[ESCALATE: DOCTOR_REQUIRED]"

**Example 3: Appointment Booking (Safe)**
User: "I want to schedule a cleaning"
Alex: "Hey! I'd love to help you schedule that cleaning. Let me check 
what's available...

*checking our calendar*

Great news! I have several options:
- Monday, Oct 7 at 10:00 AM
- Tuesday, Oct 8 at 2:00 PM
- Thursday, Oct 10 at 9:00 AM

Which one works best for you?

Also, what's the best phone number to reach you at? 😊"

**Example 4: Billing Question (Safe)**
User: "How much does a cleaning cost?"
Alex: "Great question! A standard cleaning typically costs $120-150, 
depending on what's needed during your visit.

If you have dental insurance, it might cover part or all of it - 
many plans cover 100% of preventive care like cleanings!

Would you like me to:
1. Check your specific insurance coverage?
2. Book a cleaning appointment?
3. Explain our payment plans?

What would help you most? 😊"

**Example 5: General Info (Safe)**
User: "What are your hours?"
Alex: "Hey! Our clinic hours are:
- Sunday to Thursday: 8:00 AM to 7:00 PM
- Friday: 8:00 AM to 2:00 PM
- Saturday: Closed

We're pretty flexible with scheduling! Would you like to book an 
appointment? I can check what's available for you. 😊"

═══════════════════════════════════════════════════════════════════
🎯  REMEMBER
═══════════════════════════════════════════════════════════════════

1. **Safety First** - When in doubt, escalate to doctor
2. **Be Human** - Natural, warm, empathetic conversation
3. **Be Proactive** - Offer solutions, don't just answer
4. **Be Multilingual** - Switch seamlessly between languages
5. **Be Compliant** - Follow medical safety rules STRICTLY
6. **Document Everything** - All conversations are logged

You're not just a chatbot - you're the friendly face of the clinic who 
makes sure patients get the right help at the right time! 😊

═══════════════════════════════════════════════════════════════════
"""

    def __init__(self, demo_mode: bool = False):
        """
        Initialize Alex agent.
        
        Args:
            demo_mode: If True, Alex operates in Interactive Demo mode for potential customers
        """
        self.demo_mode = demo_mode
        
        # Select system prompt based on mode
        if demo_mode:
            self.system_prompt = ALEX_DEMO_SYSTEM_PROMPT
            logger.info("Alex initialized in DEMO MODE")
        else:
            self.system_prompt = self.SYSTEM_PROMPT
            logger.info("Alex initialized in PRODUCTION MODE")
        
        # Define tools based on mode
        if demo_mode:
            # Demo mode tools - use demo data
            self.tools = [
                # Demo knowledge for product questions
                search_demo_knowledge_tool,
                # Demo patient management
                get_demo_patient_tool,
                # Demo appointments
                get_demo_appointments_tool,
                get_demo_available_slots_tool,
                book_demo_appointment_tool,
                # Demo billing
                get_demo_invoices_tool,
                get_demo_financial_summary_tool,
                # Demo clinic info
                get_demo_clinic_info_tool,
            ]
        else:
            # Production mode tools - use real Odoo data
            self.tools = [
            # Patient management (Phase 5.5 Week 1 Day 1-2)
            create_patient_tool,
            update_patient_info_tool,
            get_patient_full_context_tool,
            add_patient_note_tool,
            # Communications (Phase 5.5 Week 1 Day 3-4)
            send_sms_tool,
            send_email_tool,
            send_telegram_message_tool,
            # Advanced Telegram (Phase 3 MVP)
            send_telegram_message_with_buttons_tool,
            send_telegram_rich_message_tool,
            send_telegram_document_tool,
            send_telegram_photo_tool,
            handle_telegram_callback_tool,
            # Financial (Phase 5.5 Week 1 Day 5-6)
            process_payment_tool,
            create_payment_plan_tool,
            check_insurance_coverage_tool,
            # Advanced Scheduling (Phase 5.5 Week 1 Day 7)
            bulk_reschedule_appointments_tool,
            manage_waitlist_tool,
            # Appointments (existing)
            get_available_slots_tool,
            create_appointment_tool,
            get_my_appointments,
            book_appointment,
            get_available_appointment_slots,
            # Billing
            get_patient_invoices_tool,
            get_invoice_details_tool,
            # Knowledge
            search_general_knowledge_tool,
        ]
        
        # Bind tools to LLM
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=0.7,  # Natural conversation
            api_key=settings.OPENAI_API_KEY,
        ).bind_tools(self.tools)
    
    @handle_agent_errors
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message with medical safety checks.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with Alex's response
        """
        # Check rate limit
        user_id = state.get("user_id", "unknown")
        if not rate_limiter.check_rate_limit(state, user_id):
            retry_after = rate_limiter.get_retry_after(state, user_id)
            raise RateLimitError(f"Rate limit exceeded. Try again in {retry_after:.1f} seconds.")
        
        messages = state.get("messages", [])
        last_message = messages[-1].content if messages else ""
        
        # Get user context for RBAC
        user_role = state.get("user_role", "patient")
        
        # BUG #27 FIX: Input sanitization for prompt injection protection
        from app.core.security import sanitize_input
        sanitization_result = sanitize_input(
            last_message,
            user_role=user_role,
            context="agent_interaction"
        )
        
        # Block or sanitize malicious input
        if not sanitization_result["is_safe"]:
            if sanitization_result["action"] == "block":
                logger.warning(
                    f"Prompt injection attack blocked for user {user_id}: "
                    f"{sanitization_result['threat_type']} (confidence: {sanitization_result['confidence']:.2f})"
                )
                return {
                    **state,
                    "messages": messages + [AIMessage(
                        content="I'm sorry, but I detected potentially unsafe content in your message. "
                        "Please rephrase your request. If you need help, please contact our support team."
                    )]
                }
            elif sanitization_result["action"] == "sanitize":
                # Use sanitized input instead of original
                last_message = sanitization_result["sanitized_input"]
                logger.info(
                    f"Input sanitized for user {user_id}: {sanitization_result['threat_type']}"
                )
        
        # CRITICAL: Check for medical escalation needs
        escalation_level = self._check_escalation(last_message)
        
        # Check if user is asking about specific topics that need tools
        tool_results = []
        
        # Patient search inquiry
        if any(word in last_message.lower() for word in ["find patient", "search patient", "patient named", "patient called", "חפש מטופל", "מטופל בשם"]):
            logger.info(f"Alex detected patient search inquiry for user {user_id}")
            # Extract patient name from message (simple extraction)
            import re
            name_match = re.search(r'(?:named|called|בשם)\s+([A-Za-z\u0590-\u05FF\s]+)', last_message, re.IGNORECASE)
            if name_match:
                patient_name = name_match.group(1).strip()
                search_result = search_patient_odoo(
                    name=patient_name,
                    requesting_user_id=user_id,
                    requesting_user_role=user_role
                )
                tool_results.append(f"🔍 *Searching for patient...*\n\n{search_result}")
        
        # Patient details inquiry
        if any(word in last_message.lower() for word in ["patient details", "patient info", "show patient", "פרטי מטופל", "מידע על מטופל"]):
            logger.info(f"Alex detected patient details inquiry for user {user_id}")
            # Extract patient ID from message (simple extraction)
            import re
            id_match = re.search(r'(?:id|מזהה)[\s:]*(\d+)', last_message, re.IGNORECASE)
            if id_match:
                patient_id = int(id_match.group(1))
                details_result = get_patient_details_odoo(
                    patient_id=patient_id,
                    requesting_user_id=user_id,
                    requesting_user_role=user_role
                )
                tool_results.append(f"📋 *Retrieving patient details...*\n\n{details_result}")
        
        # Doctors list inquiry
        if any(word in last_message.lower() for word in ["doctors", "dentists", "who are the doctors", "available doctors", "רופאים", "רופאי שיניים"]):
            logger.info(f"Alex detected doctors list inquiry for user {user_id}")
            doctors_result = get_doctors_list_odoo(
                requesting_user_id=user_id,
                requesting_user_role=user_role
            )
            tool_results.append(f"👨‍⚕️ *Getting list of doctors...*\n\n{doctors_result}")
        
        # Scheduling inquiry (using existing mock tool for now)
        if any(word in last_message.lower() for word in ["available", "availability", "when", "schedule", "book", "appointment", "פנוי", "תור"]):
            logger.info(f"Alex detected scheduling inquiry for user {user_id}")
            slots_result = get_available_slots_tool(days_ahead=7)
            tool_results.append(f"📅 *Checking calendar...*\n\n{slots_result}")
        
        # Billing inquiry (using existing mock tool for now)
        if any(word in last_message.lower() for word in ["invoice", "bill", "payment", "owe", "balance", "חשבונית", "תשלום"]):
            logger.info(f"Alex detected billing inquiry for user {user_id}")
            if "my invoice" in last_message.lower() or "my bill" in last_message.lower():
                # Demo patient for testing
                invoice_result = get_patient_invoices_tool("John Doe")
                tool_results.append(f"💰 *Checking your account...*\n\n{invoice_result}")
        
        # Build conversation
        conversation = [SystemMessage(content=self.system_prompt)]
        
        # Add tool results if available
        if tool_results:
            for result in tool_results:
                conversation.append(SystemMessage(content=result))
        
        # Add escalation context if needed
        if escalation_level:
            escalation_instruction = SystemMessage(content=f"""
ESCALATION DETECTED: {escalation_level}

You MUST follow the escalation protocol for {escalation_level} level.
Include [ESCALATE: {escalation_level}] at the end of your response.
""")
            conversation.append(escalation_instruction)
        
        conversation.extend(messages)
        
        # Generate response with retry logic and tool calling support
        logger.info(f"Alex processing message for user {user_id} (escalation: {escalation_level or 'none'})")
        
        # Agent loop: Keep calling LLM until it's done (no more tool calls)
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            response = retry_handler.execute(self.llm.invoke, conversation)
            
            # Check if LLM wants to call tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info(f"Alex calling {len(response.tool_calls)} tools")
                
                # Add AI message with tool calls to conversation
                conversation.append(response)
                
                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call.name
                    tool_args = tool_call.args
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Find and execute the tool
                    tool_result = None
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = tool.invoke(tool_args)
                            except Exception as e:
                                tool_result = f"Error executing {tool_name}: {str(e)}"
                                logger.error(f"Tool execution error: {e}")
                            break
                    
                    if tool_result is None:
                        tool_result = f"Tool {tool_name} not found"
                    
                    # Add tool result to conversation
                    from langchain_core.messages import ToolMessage
                    conversation.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call.id
                    ))
                
                iteration += 1
            else:
                # No more tool calls, we're done
                break
        
        # Check if escalation tag is present
        requires_human = "[ESCALATE:" in response.content if hasattr(response, 'content') else False
        
        if requires_human:
            logger.warning(f"Alex escalating to doctor for user {user_id}: {escalation_level}")
        
        # Ensure response has content (fallback for empty responses)
        if not hasattr(response, 'content') or not response.content or response.content.strip() == "":
            logger.warning("Alex generated empty response, using fallback")
            from langchain_core.messages import AIMessage
            if self.demo_mode:
                fallback_content = "שלום! אני אלכס, העוזר הדיגיטלי של DentaFlow. אשמח לעזור לך! נסה לשאול אותי על תכונות המערכת, קביעת תורים, או מידע על מטופלים."
            else:
                fallback_content = "I'm here to help! Please let me know what you need assistance with."
            response = AIMessage(content=fallback_content)
        
        # BUG #29 FIX: Output validation for PII/PHI protection
        from app.core.security import validate_output
        validation_result = validate_output(
            response.content,
            user_role=user_role,
            patient_id=state.get("patient_id"),
            context="patient_chat"
        )
        
        # Use sanitized output if needed
        if not validation_result["is_safe"]:
            if validation_result["action"] == "sanitize":
                logger.warning(
                    f"Output sanitized for user {user_id}: {validation_result['reason']}"
                )
                # Replace response content with sanitized version
                response = AIMessage(content=validation_result["sanitized_output"])
            elif validation_result["action"] == "block":
                logger.error(
                    f"Output blocked for user {user_id}: {validation_result['reason']}"
                )
                # Replace with safe generic message
                response = AIMessage(
                    content="I apologize, but I cannot provide that information. "
                    "Please contact your clinic directly for assistance."
                )
        
        # Update state
        state["messages"] = messages + [response]
        state["current_agent"] = "alex"
        state["requires_human"] = requires_human
        state["escalation_level"] = escalation_level
        
        return state
    
    def _check_escalation(self, message: str) -> Optional[str]:
        """
        Check if message requires medical escalation.
        
        Args:
            message: User message
            
        Returns:
            Escalation level or None
        """
        message_lower = message.lower()
        
        # Check for emergency keywords
        for keyword in self.EMERGENCY_KEYWORDS:
            if keyword in message_lower:
                return "EMERGENCY"
        
        # Check for doctor-required keywords
        for keyword in self.DOCTOR_REQUIRED_KEYWORDS:
            if keyword in message_lower:
                return "DOCTOR_REQUIRED"
        
        # Check for pain level
        if "pain" in message_lower:
            # Try to extract pain level (1-10)
            import re
            pain_match = re.search(r'(\d+)\s*/\s*10|pain.*?(\d+)', message_lower)
            if pain_match:
                pain_level = int(pain_match.group(1) or pain_match.group(2))
                if pain_level >= 8:
                    return "EMERGENCY"
                elif pain_level >= 5:
                    return "DOCTOR_REQUIRED"
        
        return None
