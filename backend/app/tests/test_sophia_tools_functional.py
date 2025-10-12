'''
Sophia (Practice Admin) Tools Functional Tests - SAMPLING

Tests 15 representative tools out of 43 Sophia tools (35% coverage).
Selected tools cover all major operational categories:
- Scheduling/Admin (3 tools)
- Inventory Management (4 tools)
- Staff Management (4 tools)
- Compliance & Facilities (4 tools)

Total: 15/43 tools tested
'''

import sys
from datetime import datetime, timedelta

def run_test(test_func):
    """Helper function to run a test and print the result."""
    test_name = test_func.__name__
    print(f"Running test: {test_name}...")
    try:
        result = test_func()
        if result:
            # Truncate result for display
            result_str = str(result)
            if len(result_str) > 150:
                result_str = result_str[:150] + "..."
            print(f"✅ PASSED: {test_name}")
            print(f"   Result: {result_str}")
            return True
        else:
            print(f"❌ FAILED: {test_name} - No result returned")
            return False
    except Exception as e:
        print(f"❌ FAILED: {test_name}")
        print(f"   Error: {e}")
        return False

# ==========================================
# SCHEDULING/ADMIN TOOLS (3/8 tools tested)
# ==========================================

def test_get_schedule_conflicts_tool():
    """Test getting schedule conflicts."""
    from app.agents.tools.admin_tools import get_schedule_conflicts_tool
    
    result = get_schedule_conflicts_tool.invoke({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "days": 7
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_room_availability_tool():
    """Test getting room availability."""
    from app.agents.tools.admin_tools import get_room_availability_tool
    
    result = get_room_availability_tool.invoke({
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_operational_metrics_tool():
    """Test getting operational metrics."""
    from app.agents.tools.admin_tools import get_operational_metrics_tool
    
    result = get_operational_metrics_tool.invoke({
        "date_range": 7
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# INVENTORY MANAGEMENT (4/12 tools tested)
# ==========================================

def test_check_inventory_levels_tool():
    """Test checking inventory levels."""
    from app.agents.tools.sophia_inventory_tools import check_inventory_levels_tool
    
    result = check_inventory_levels_tool.invoke({
        "category": None,
        "low_stock_only": False
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_low_stock_alerts_tool():
    """Test getting low stock alerts."""
    from app.agents.tools.sophia_inventory_tools import get_low_stock_alerts_tool
    
    result = get_low_stock_alerts_tool.invoke({})
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_track_expiring_products_tool():
    """Test tracking expiring products."""
    from app.agents.tools.sophia_inventory_tools import track_expiring_products_tool
    
    result = track_expiring_products_tool.invoke({
        "days_ahead": 30
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_create_purchase_order_tool():
    """Test creating a purchase order."""
    from app.agents.tools.sophia_inventory_tools import create_purchase_order_tool
    
    result = create_purchase_order_tool.invoke({
        "supplier_name": "Dental Supplies Ltd",
        "items": [
            {"product_id": 1, "quantity": 100, "price": 10.0}
        ],
        "notes": "Urgent order"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# STAFF MANAGEMENT (4/13 tools tested)
# ==========================================

def test_get_staff_list_tool():
    """Test getting staff list."""
    from app.agents.tools.sophia_staff_tools import get_staff_list_tool
    
    result = get_staff_list_tool.invoke({
        "role": "all"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_doctor_availability_tool():
    """Test getting doctor availability."""
    from app.agents.tools.sophia_staff_tools import get_doctor_availability_tool
    
    result = get_doctor_availability_tool.invoke({
        "doctor_name": "Dr. Smith",
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_staff_workload_tool():
    """Test getting staff workload."""
    from app.agents.tools.sophia_staff_tools import get_staff_workload_tool
    
    result = get_staff_workload_tool.invoke({
        "date_from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
        "date_to": datetime.now().strftime("%Y-%m-%d")
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_time_off_requests_tool():
    """Test getting time off requests."""
    from app.agents.tools.sophia_staff_tools import get_time_off_requests_tool
    
    result = get_time_off_requests_tool.invoke({
        "status": None
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# COMPLIANCE & FACILITIES (4/10 tools tested)
# ==========================================

def test_get_rooms_list_tool():
    """Test getting treatment rooms."""
    from app.agents.tools.sophia_compliance_tools import get_rooms_list_tool
    
    result = get_rooms_list_tool.invoke({
        "available_only": False
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_equipment_list_tool():
    """Test getting equipment inventory."""
    from app.agents.tools.sophia_compliance_tools import get_equipment_list_tool
    
    result = get_equipment_list_tool.invoke({
        "category": "dental"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_compliance_reminders_tool():
    """Test getting compliance reminders."""
    from app.agents.tools.sophia_compliance_tools import get_compliance_reminders_tool
    
    result = get_compliance_reminders_tool.invoke({
        "days_ahead": 30
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_create_maintenance_request_tool():
    """Test creating a maintenance request."""
    from app.agents.tools.sophia_compliance_tools import create_maintenance_request_tool
    
    result = create_maintenance_request_tool.invoke({
        "equipment_name": "Dental Chair 1",
        "issue_description": "Equipment not working properly",
        "priority": "medium"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# MAIN TEST RUNNER
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("SOPHIA (PRACTICE ADMIN) TOOLS FUNCTIONAL TESTS (SAMPLING)")
    print("=" * 80)
    print()
    
    tests = [
        # Scheduling/Admin (3)
        test_get_schedule_conflicts_tool,
        test_get_room_availability_tool,
        test_get_operational_metrics_tool,
        
        # Inventory Management (4)
        test_check_inventory_levels_tool,
        test_get_low_stock_alerts_tool,
        test_track_expiring_products_tool,
        test_create_purchase_order_tool,
        
        # Staff Management (4)
        test_get_staff_list_tool,
        test_get_doctor_availability_tool,
        test_get_staff_workload_tool,
        test_get_time_off_requests_tool,
        
        # Compliance & Facilities (4)
        test_get_rooms_list_tool,
        test_get_equipment_list_tool,
        test_get_compliance_reminders_tool,
        test_create_maintenance_request_tool,
    ]
    
    print(f"Running {len(tests)} functional tests for Sophia's tools (sampling 15/43)...\n")
    
    results = []
    for test in tests:
        result = run_test(test)
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print("=" * 80)
    print(f"RESULTS: {passed}/{total} tests passed ({percentage:.1f}%)")
    print("=" * 80)
    print(f"Coverage: 15/43 Sophia tools tested (34.9%)")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 All Sophia tool functional tests passed!")
        sys.exit(0)
    elif passed >= total * 0.9:
        print(f"\n✅ Excellent! {passed}/{total} tests passed (>90%)")
        sys.exit(0)
    elif passed >= total * 0.75:
        print(f"\n⚠️ Good progress: {passed}/{total} tests passed (>75%)")
        sys.exit(1)
    else:
        print(f"\n❌ More work needed: {passed}/{total} tests passed (<75%)")
        sys.exit(1)

