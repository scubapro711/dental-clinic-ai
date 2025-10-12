'''
Marcus (CFO) Tools Functional Tests - SAMPLING

Tests 8 representative tools out of 23 Marcus tools (35% coverage).
Selected tools cover all major financial categories:
- Revenue Analysis (2 tools)
- Invoice Management (2 tools)
- Tax Tools (2 tools)
- Budgeting (1 tool)
- Accountant Referral (1 tool)

Total: 8/23 tools tested
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
# REVENUE ANALYSIS (2/7 tools tested)
# ==========================================

def test_get_revenue_overview():
    """Test getting revenue overview."""
    from app.agents.tools.marcus_financial_tools import get_revenue_overview
    
    date_to = datetime.now().strftime("%Y-%m-%d")
    date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    result = get_revenue_overview.invoke({
        "date_from": date_from,
        "date_to": date_to
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_get_outstanding_invoices():
    """Test getting outstanding invoices."""
    from app.agents.tools.marcus_financial_tools import get_outstanding_invoices
    
    result = get_outstanding_invoices.invoke({})
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# INVOICE MANAGEMENT (2/6 tools tested)
# ==========================================

def test_create_invoice_tool():
    """Test creating an invoice."""
    from app.agents.tools.marcus_financial_tools import create_invoice_tool
    
    result = create_invoice_tool.invoke({
        "patient_id": 1,
        "treatment_ids": [1, 2]  # List of treatment IDs
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

def test_record_payment_tool():
    """Test recording a payment."""
    from app.agents.tools.marcus_financial_tools import record_payment_tool
    
    result = record_payment_tool.invoke({
        "invoice_id": 1,
        "amount": 300.0,
        "payment_method": "credit_card",
        "payment_date": datetime.now().strftime("%Y-%m-%d")
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# TAX TOOLS (2/4 tools tested)
# ==========================================

def test_calculate_income_tax():
    """Test calculating income tax."""
    from app.agents.tools.tax_tools import calculate_income_tax
    
    result = calculate_income_tax.invoke({
        "annual_income": 500000.0,
        "entity_type": "individual"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    assert "מס הכנסה" in result or "tax" in result.lower(), "Missing tax info"
    return result

def test_calculate_vat_amount():
    """Test calculating VAT."""
    from app.agents.tools.tax_tools import calculate_vat_amount
    
    result = calculate_vat_amount.invoke({
        "amount": 1000.0,
        "treatment_type": "aesthetic"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    assert "מע\"מ" in result or "VAT" in result, "Missing VAT info"
    return result

# ==========================================
# BUDGETING (1/2 tools tested)
# ==========================================

def test_get_budget_tool():
    """Test getting budget information."""
    from app.agents.tools.marcus_financial_tools import get_budget_tool
    
    result = get_budget_tool.invoke({
        "department": "clinical"  # Required parameter
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# ACCOUNTANT REFERRAL (1/1 tools tested)
# ==========================================

def test_find_accountant():
    """Test finding an accountant."""
    from app.agents.tools.accountant_referral import find_accountant
    
    result = find_accountant.invoke({
        "specialty": "dental_clinic",
        "location": "Tel Aviv"
    })
    
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 10, "Result too short"
    return result

# ==========================================
# MAIN TEST RUNNER
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("MARCUS (CFO) TOOLS FUNCTIONAL TESTS (SAMPLING)")
    print("=" * 80)
    print()
    
    tests = [
        # Revenue Analysis (2)
        test_get_revenue_overview,
        test_get_outstanding_invoices,
        
        # Invoice Management (2)
        test_create_invoice_tool,
        test_record_payment_tool,
        
        # Tax Tools (2)
        test_calculate_income_tax,
        test_calculate_vat_amount,
        
        # Budgeting (1)
        test_get_budget_tool,
        
        # Accountant Referral (1)
        test_find_accountant,
    ]
    
    print(f"Running {len(tests)} functional tests for Marcus's tools (sampling 8/23)...\n")
    
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
    print(f"Coverage: 8/23 Marcus tools tested (34.8%)")
    print("=" * 80)
    
    if passed == total:
        print("\n🎉 All Marcus tool functional tests passed!")
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

