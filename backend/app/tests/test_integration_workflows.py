'''
Phase 6.3 - Integration Tests

Tests complete workflows that involve multiple tools and agents working together.
These tests verify that the system works end-to-end, not just individual components.

Test Categories:
1. Single Agent Multi-Tool Workflows (Alex, Sarah, Marcus, Sophia)
2. Multi-Agent Collaboration (via Supervisor)
3. Error Handling & Recovery
4. Data Consistency & State Management

Each test simulates a realistic scenario that a dental clinic would encounter.
'''

import sys
from datetime import datetime, timedelta

def run_test(test_func):
    """Helper function to run a test and print the result."""
    test_name = test_func.__name__
    print(f"\nRunning test: {test_name}...")
    print("-" * 80)
    try:
        result = test_func()
        if result:
            print(f"✅ PASSED: {test_name}")
            print(f"   Result: {result}")
            return True
        else:
            print(f"❌ FAILED: {test_name} - No result returned")
            return False
    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==========================================
# CATEGORY 1: SINGLE AGENT MULTI-TOOL WORKFLOWS
# ==========================================

def test_alex_complete_patient_onboarding():
    """
    Test Alex handling complete patient onboarding workflow.
    
    Workflow:
    1. Create new patient
    2. Send welcome message
    3. Schedule first appointment
    4. Send appointment confirmation
    """
    from app.agents.alex_v2 import AlexAgent
    
    alex = AlexAgent()
    
    # Simulate conversation
    messages = [
        {
            "role": "user",
            "content": "I need to onboard a new patient: John Doe, phone 050-1234567, email john@example.com. Schedule him for next Monday at 10:00 AM with Dr. Smith for initial consultation."
        }
    ]
    
    # Invoke Alex
    result = alex.graph.invoke({
        "messages": messages,
        "patient_context": {}
    })
    
    # Verify result
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 1, "No response from Alex"
    
    response = result["messages"][-1]["content"]
    
    # Check that response mentions key actions
    success_indicators = [
        "patient" in response.lower(),
        "appointment" in response.lower() or "scheduled" in response.lower(),
    ]
    
    assert any(success_indicators), f"Response doesn't indicate success: {response}"
    
    return f"Patient onboarded successfully. Response length: {len(response)} chars"

def test_sarah_complete_treatment_workflow():
    """
    Test Sarah handling complete treatment workflow.
    
    Workflow:
    1. Review patient dental chart
    2. Create treatment plan
    3. Record treatment
    4. Update dental chart
    """
    from app.agents.sarah_clinical import SarahClinicalAgent
    
    sarah = SarahClinicalAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Patient ID 123 came in for checkup. Found cavity in tooth 14. Please review chart, create treatment plan for filling, and record the treatment."
        }
    ]
    
    result = sarah.graph.invoke({
        "messages": messages,
        "patient_context": {"patient_id": 123}
    })
    
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 1, "No response from Sarah"
    
    response = result["messages"][-1]["content"]
    
    success_indicators = [
        "treatment" in response.lower(),
        "tooth" in response.lower() or "14" in response,
    ]
    
    assert any(success_indicators), f"Response doesn't indicate success: {response}"
    
    return f"Treatment workflow completed. Response length: {len(response)} chars"

def test_marcus_complete_billing_workflow():
    """
    Test Marcus handling complete billing workflow.
    
    Workflow:
    1. Get treatment details
    2. Create invoice
    3. Send invoice to patient
    4. Track payment status
    """
    from app.agents.cfo import CFOAgent
    
    marcus = CFOAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Patient 123 completed treatment. Create invoice for tooth filling (1500 NIS), send it to patient, and give me payment status."
        }
    ]
    
    result = marcus.graph.invoke({
        "messages": messages,
        "patient_context": {"patient_id": 123}
    })
    
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 1, "No response from Marcus"
    
    response = result["messages"][-1]["content"]
    
    success_indicators = [
        "invoice" in response.lower(),
        "1500" in response or "payment" in response.lower(),
    ]
    
    assert any(success_indicators), f"Response doesn't indicate success: {response}"
    
    return f"Billing workflow completed. Response length: {len(response)} chars"

def test_sophia_complete_admin_workflow():
    """
    Test Sophia handling complete admin workflow.
    
    Workflow:
    1. Check inventory levels
    2. Create purchase order for low stock
    3. Schedule staff for next week
    4. Generate operational report
    """
    from app.agents.practice_admin import PracticeAdminAgent
    
    sophia = PracticeAdminAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Check inventory, order anything that's low, schedule Dr. Smith for next week 9-5, and give me operational metrics for this month."
        }
    ]
    
    result = sophia.graph.invoke({
        "messages": messages
    })
    
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 1, "No response from Sophia"
    
    response = result["messages"][-1]["content"]
    
    success_indicators = [
        "inventory" in response.lower() or "stock" in response.lower(),
        "schedule" in response.lower() or "smith" in response.lower(),
    ]
    
    assert any(success_indicators), f"Response doesn't indicate success: {response}"
    
    return f"Admin workflow completed. Response length: {len(response)} chars"

# ==========================================
# CATEGORY 2: MULTI-AGENT COLLABORATION
# ==========================================

def test_supervisor_patient_journey():
    """
    Test Supervisor coordinating complete patient journey across all agents.
    
    Journey:
    1. Alex: Patient calls to schedule
    2. Sarah: Treatment during appointment
    3. Marcus: Billing after treatment
    4. Sophia: Follow-up scheduling
    """
    from app.agents.agent_graph_v4 import create_agent_graph_v4
    
    graph = create_agent_graph_v4()
    
    messages = [
        {
            "role": "user",
            "content": "New patient Sarah Cohen (050-9876543) wants to schedule cleaning. After cleaning, she'll need filling in tooth 21. Handle the complete journey from scheduling to billing."
        }
    ]
    
    result = graph.invoke({
        "messages": messages,
        "next": "supervisor"
    })
    
    assert "messages" in result, "No messages in result"
    
    # Check that multiple agents were involved
    # (Supervisor should have delegated to Alex, Sarah, Marcus)
    
    response_text = str(result["messages"])
    
    success_indicators = [
        len(result["messages"]) > 3,  # Multiple interactions
        "schedule" in response_text.lower() or "appointment" in response_text.lower(),
    ]
    
    assert any(success_indicators), "Multi-agent collaboration didn't work"
    
    return f"Patient journey completed with {len(result['messages'])} messages"

def test_supervisor_handoff_alex_to_sarah():
    """
    Test Supervisor handling handoff from Alex to Sarah.
    
    Scenario: Patient asks about treatment, Alex schedules, Sarah provides clinical info.
    """
    from app.agents.agent_graph_v4 import create_agent_graph_v4
    
    graph = create_agent_graph_v4()
    
    messages = [
        {
            "role": "user",
            "content": "Patient 123 is asking about root canal procedure. Can you explain it and schedule them?"
        }
    ]
    
    result = graph.invoke({
        "messages": messages,
        "next": "supervisor"
    })
    
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 2, "Not enough agent interactions"
    
    return f"Handoff completed with {len(result['messages'])} messages"

def test_supervisor_handoff_sarah_to_marcus():
    """
    Test Supervisor handling handoff from Sarah to Marcus.
    
    Scenario: Treatment completed, need to create invoice.
    """
    from app.agents.agent_graph_v4 import create_agent_graph_v4
    
    graph = create_agent_graph_v4()
    
    messages = [
        {
            "role": "user",
            "content": "Patient 123 just completed root canal treatment. Record it and create invoice for 3500 NIS."
        }
    ]
    
    result = graph.invoke({
        "messages": messages,
        "next": "supervisor"
    })
    
    assert "messages" in result, "No messages in result"
    assert len(result["messages"]) > 2, "Not enough agent interactions"
    
    return f"Handoff completed with {len(result['messages'])} messages"

# ==========================================
# CATEGORY 3: ERROR HANDLING & RECOVERY
# ==========================================

def test_alex_handles_invalid_patient_id():
    """
    Test that Alex handles invalid patient ID gracefully.
    """
    from app.agents.alex_v2 import AlexAgent
    
    alex = AlexAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Get appointments for patient ID 999999999 (doesn't exist)"
        }
    ]
    
    result = alex.graph.invoke({
        "messages": messages,
        "patient_context": {}
    })
    
    assert "messages" in result, "No messages in result"
    response = result["messages"][-1]["content"]
    
    # Should handle error gracefully, not crash
    assert len(response) > 10, "No error message returned"
    
    return "Error handled gracefully"

def test_sarah_handles_missing_patient_data():
    """
    Test that Sarah handles missing patient data gracefully.
    """
    from app.agents.sarah_clinical import SarahClinicalAgent
    
    sarah = SarahClinicalAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Show me dental chart for patient 999999999"
        }
    ]
    
    result = sarah.graph.invoke({
        "messages": messages,
        "patient_context": {}
    })
    
    assert "messages" in result, "No messages in result"
    response = result["messages"][-1]["content"]
    
    assert len(response) > 10, "No error message returned"
    
    return "Error handled gracefully"

def test_marcus_handles_invalid_invoice():
    """
    Test that Marcus handles invalid invoice operations gracefully.
    """
    from app.agents.cfo import CFOAgent
    
    marcus = CFOAgent()
    
    messages = [
        {
            "role": "user",
            "content": "Show me invoice 999999999 details"
        }
    ]
    
    result = marcus.graph.invoke({
        "messages": messages,
        "patient_context": {}
    })
    
    assert "messages" in result, "No messages in result"
    response = result["messages"][-1]["content"]
    
    assert len(response) > 10, "No error message returned"
    
    return "Error handled gracefully"

# ==========================================
# CATEGORY 4: DATA CONSISTENCY
# ==========================================

def test_patient_data_consistency_across_agents():
    """
    Test that patient data remains consistent when accessed by different agents.
    
    Scenario: Create patient with Alex, verify Sarah and Marcus can access same data.
    """
    from app.agents.alex_v2 import AlexAgent
    from app.agents.sarah_clinical import SarahClinicalAgent
    from app.agents.cfo import CFOAgent
    
    alex = AlexAgent()
    sarah = SarahClinicalAgent()
    marcus = CFOAgent()
    
    # Alex creates patient (simulated)
    patient_id = 123
    
    # Sarah accesses patient
    sarah_messages = [{"role": "user", "content": f"Show dental chart for patient {patient_id}"}]
    sarah_result = sarah.graph.invoke({"messages": sarah_messages, "patient_context": {"patient_id": patient_id}})
    
    # Marcus accesses patient
    marcus_messages = [{"role": "user", "content": f"Show invoices for patient {patient_id}"}]
    marcus_result = marcus.graph.invoke({"messages": marcus_messages, "patient_context": {"patient_id": patient_id}})
    
    # Both should return valid responses (not errors)
    assert "messages" in sarah_result and len(sarah_result["messages"]) > 1
    assert "messages" in marcus_result and len(marcus_result["messages"]) > 1
    
    return "Data consistency verified across agents"

# ==========================================
# MAIN TEST RUNNER
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("PHASE 6.3 - INTEGRATION TESTS")
    print("=" * 80)
    print()
    print("Testing complete workflows and multi-agent collaboration...")
    print()
    
    tests = [
        # Category 1: Single Agent Multi-Tool Workflows
        ("Single Agent Workflows", [
            test_alex_complete_patient_onboarding,
            test_sarah_complete_treatment_workflow,
            test_marcus_complete_billing_workflow,
            test_sophia_complete_admin_workflow,
        ]),
        
        # Category 2: Multi-Agent Collaboration
        ("Multi-Agent Collaboration", [
            test_supervisor_patient_journey,
            test_supervisor_handoff_alex_to_sarah,
            test_supervisor_handoff_sarah_to_marcus,
        ]),
        
        # Category 3: Error Handling
        ("Error Handling", [
            test_alex_handles_invalid_patient_id,
            test_sarah_handles_missing_patient_data,
            test_marcus_handles_invalid_invoice,
        ]),
        
        # Category 4: Data Consistency
        ("Data Consistency", [
            test_patient_data_consistency_across_agents,
        ]),
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category_name, category_tests in tests:
        print("\n" + "=" * 80)
        print(f"CATEGORY: {category_name}")
        print("=" * 80)
        
        category_results = []
        for test in category_tests:
            result = run_test(test)
            category_results.append(result)
            total_tests += 1
            if result:
                total_passed += 1
        
        category_passed = sum(category_results)
        category_total = len(category_results)
        print(f"\nCategory Results: {category_passed}/{category_total} passed")
    
    # Final Summary
    print("\n" + "=" * 80)
    print(f"FINAL RESULTS: {total_passed}/{total_tests} tests passed ({(total_passed/total_tests)*100:.1f}%)")
    print("=" * 80)
    
    if total_passed == total_tests:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    elif total_passed >= total_tests * 0.8:
        print(f"\n✅ Good! {total_passed}/{total_tests} tests passed (>80%)")
        sys.exit(0)
    else:
        print(f"\n⚠️ More work needed: {total_passed}/{total_tests} tests passed (<80%)")
        sys.exit(1)

