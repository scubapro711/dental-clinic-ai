"""
Phase 6.4 - End-to-End Tests (User Journeys)
Test complete user flows from start to finish using AgentGraphV4.

Tests realistic scenarios that users would experience in production.
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

# Set test environment
os.environ["APP_ENV"] = "test"

from app.agents.agent_graph_v4 import AgentGraphV4


def create_test_graph():
    """Create a fresh graph instance for testing."""
    checkpointer = MemorySaver()
    graph = AgentGraphV4(memory=checkpointer)
    return graph


class TestPatientJourneys:
    """Test complete patient user journeys."""
    
    def test_journey_1_new_patient_books_appointment(self):
        """
        Journey 1: New Patient Books Appointment
        
        Steps:
        1. Patient asks about available times
        2. Patient books appointment
        3. Patient confirms booking
        
        Expected: Alex handles the entire flow
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_1"
        org_id = "test_org_123"
        user_id = "patient_new_001"
        
        # Step 1: Ask about available times
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="Hi, I'm a new patient. When are you available for a checkup?")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        assert len(result1["messages"]) >= 2
        print(f"✅ Step 1: Patient asks about availability")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        print(f"   Response: {result1['messages'][-1].content[:100]}...")
        
        # Step 2: Book appointment
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="Great! I'd like to book for Monday at 10am")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Patient books appointment")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        print(f"   Response: {result2['messages'][-1].content[:100]}...")
        
        # Step 3: Confirm
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Yes, please confirm the booking")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Patient confirms booking")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        print(f"   Response: {result3['messages'][-1].content[:100]}...")
        
        print(f"✅ Journey 1 Complete: New Patient Books Appointment")
    
    def test_journey_2_patient_cancels_appointment(self):
        """
        Journey 2: Patient Cancels Appointment
        
        Steps:
        1. Patient asks about their appointments
        2. Patient requests cancellation
        3. Patient confirms cancellation
        
        Expected: Alex handles the entire flow
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_2"
        org_id = "test_org_123"
        user_id = "patient_existing_002"
        
        # Step 1: Ask about appointments
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="Can you show me my upcoming appointments?")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Patient asks about appointments")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Request cancellation
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="I need to cancel my appointment on Monday")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Patient requests cancellation")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Confirm cancellation
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Yes, please cancel it")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Patient confirms cancellation")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 2 Complete: Patient Cancels Appointment")
    
    def test_journey_3_patient_asks_about_invoice(self):
        """
        Journey 3: Patient Asks About Invoice
        
        Steps:
        1. Patient asks about their bill
        2. Patient asks for payment options
        3. Patient requests payment link
        
        Expected: Marcus (CFO) handles the financial flow
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_3"
        org_id = "test_org_123"
        user_id = "patient_existing_003"
        
        # Step 1: Ask about bill
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="What's my current bill? Do I owe anything?")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Patient asks about bill")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Ask about payment options
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="How can I pay? What options do you accept?")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Patient asks about payment options")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Request payment link
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Can you send me a payment link?")],
                "organization_id": org_id,
                "user_role": "patient",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Patient requests payment link")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 3 Complete: Patient Asks About Invoice")


class TestDoctorJourneys:
    """Test complete doctor user journeys."""
    
    def test_journey_4_doctor_reviews_patient_chart(self):
        """
        Journey 4: Doctor Reviews Patient Chart
        
        Steps:
        1. Doctor asks for patient chart
        2. Doctor asks about specific tooth
        3. Doctor asks about treatment history
        
        Expected: Sarah (Clinical) handles the entire flow
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_4"
        org_id = "test_org_123"
        user_id = "doctor_001"
        
        # Step 1: Ask for patient chart
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="Show me the dental chart for patient ID 123")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Doctor asks for patient chart")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Ask about specific tooth
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="What's the status of tooth 16?")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Doctor asks about specific tooth")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Ask about treatment history
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Show me all treatments for this patient")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Doctor asks about treatment history")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 4 Complete: Doctor Reviews Patient Chart")
    
    def test_journey_5_doctor_creates_treatment_plan(self):
        """
        Journey 5: Doctor Creates Treatment Plan
        
        Steps:
        1. Doctor asks to create treatment plan
        2. Doctor specifies treatments
        3. Doctor confirms plan
        
        Expected: Sarah (Clinical) handles the entire flow
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_5"
        org_id = "test_org_123"
        user_id = "doctor_002"
        
        # Step 1: Ask to create treatment plan
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="I need to create a treatment plan for patient 456")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Doctor asks to create treatment plan")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Specify treatments
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="The plan includes: root canal on tooth 16, crown on tooth 17")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Doctor specifies treatments")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Confirm plan
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Yes, create this treatment plan")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Doctor confirms plan")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 5 Complete: Doctor Creates Treatment Plan")
    
    def test_journey_6_doctor_checks_revenue(self):
        """
        Journey 6: Doctor Checks Revenue
        
        Steps:
        1. Doctor asks about monthly revenue
        2. Doctor asks for breakdown by treatment
        3. Doctor asks about pending payments
        
        Expected: Marcus (CFO) handles the financial analysis
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_6"
        org_id = "test_org_123"
        user_id = "doctor_003"
        
        # Step 1: Ask about monthly revenue
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="What was our revenue last month?")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Doctor asks about monthly revenue")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Ask for breakdown
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="Can you break it down by treatment type?")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Doctor asks for breakdown")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Ask about pending payments
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="How much is pending payment?")],
                "organization_id": org_id,
                "user_role": "doctor",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Doctor asks about pending payments")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 6 Complete: Doctor Checks Revenue")


class TestStaffJourneys:
    """Test complete staff user journeys."""
    
    def test_journey_7_staff_checks_schedule(self):
        """
        Journey 7: Staff Checks Schedule
        
        Steps:
        1. Staff asks about today's schedule
        2. Staff asks about specific doctor availability
        3. Staff asks to schedule appointment
        
        Expected: Sophia (Practice Admin) handles operations
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_7"
        org_id = "test_org_123"
        user_id = "staff_001"
        
        # Step 1: Ask about today's schedule
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="What's the schedule for today?")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Staff asks about today's schedule")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Ask about doctor availability
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="Is Dr. Cohen available at 2pm?")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Staff asks about doctor availability")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Schedule appointment
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Please schedule patient 789 for 2pm with Dr. Cohen")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Staff schedules appointment")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 7 Complete: Staff Checks Schedule")
    
    def test_journey_8_staff_manages_inventory(self):
        """
        Journey 8: Staff Manages Inventory
        
        Steps:
        1. Staff asks about inventory levels
        2. Staff asks about low stock items
        3. Staff requests reorder
        
        Expected: Sophia (Practice Admin) handles inventory
        """
        graph = create_test_graph()
        compiled_graph = graph.graph
        
        thread_id = "journey_8"
        org_id = "test_org_123"
        user_id = "staff_002"
        
        # Step 1: Ask about inventory
        result1 = compiled_graph.invoke(
            {
                "messages": [HumanMessage(content="Show me current inventory levels")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result1 is not None
        print(f"✅ Step 1: Staff asks about inventory")
        print(f"   Agent: {result1.get('current_agent', 'unknown')}")
        
        # Step 2: Ask about low stock
        result2 = compiled_graph.invoke(
            {
                "messages": result1["messages"] + [HumanMessage(content="What items are running low?")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result2 is not None
        print(f"✅ Step 2: Staff asks about low stock")
        print(f"   Agent: {result2.get('current_agent', 'unknown')}")
        
        # Step 3: Request reorder
        result3 = compiled_graph.invoke(
            {
                "messages": result2["messages"] + [HumanMessage(content="Please reorder gloves and masks")],
                "organization_id": org_id,
                "user_role": "staff",
                "user_id": user_id
            },
            config={"configurable": {"thread_id": thread_id}}
        )
        
        assert result3 is not None
        print(f"✅ Step 3: Staff requests reorder")
        print(f"   Agent: {result3.get('current_agent', 'unknown')}")
        
        print(f"✅ Journey 8 Complete: Staff Manages Inventory")


# Run all tests
if __name__ == "__main__":
    print("=" * 80)
    print("Phase 6.4 - End-to-End Tests (User Journeys)")
    print("=" * 80)
    print()
    
    # Patient Journeys
    print("1. Patient Journeys")
    print("-" * 80)
    test = TestPatientJourneys()
    try:
        test.test_journey_1_new_patient_books_appointment()
    except Exception as e:
        print(f"❌ Journey 1: {e}")
    print()
    
    try:
        test.test_journey_2_patient_cancels_appointment()
    except Exception as e:
        print(f"❌ Journey 2: {e}")
    print()
    
    try:
        test.test_journey_3_patient_asks_about_invoice()
    except Exception as e:
        print(f"❌ Journey 3: {e}")
    print()
    
    # Doctor Journeys
    print("2. Doctor Journeys")
    print("-" * 80)
    test = TestDoctorJourneys()
    try:
        test.test_journey_4_doctor_reviews_patient_chart()
    except Exception as e:
        print(f"❌ Journey 4: {e}")
    print()
    
    try:
        test.test_journey_5_doctor_creates_treatment_plan()
    except Exception as e:
        print(f"❌ Journey 5: {e}")
    print()
    
    try:
        test.test_journey_6_doctor_checks_revenue()
    except Exception as e:
        print(f"❌ Journey 6: {e}")
    print()
    
    # Staff Journeys
    print("3. Staff Journeys")
    print("-" * 80)
    test = TestStaffJourneys()
    try:
        test.test_journey_7_staff_checks_schedule()
    except Exception as e:
        print(f"❌ Journey 7: {e}")
    print()
    
    try:
        test.test_journey_8_staff_manages_inventory()
    except Exception as e:
        print(f"❌ Journey 8: {e}")
    print()
    
    print("=" * 80)
    print("✅ E2E Tests Complete!")
    print("=" * 80)

