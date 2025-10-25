"""
Bug #28 Fix Verification Tests: RBAC Enforcement

This test file verifies that the RBAC fallback bypass has been fixed
and that tools now properly enforce RBAC context requirements.

Author: Manus AI
Date: October 25, 2025
"""

import pytest
from app.agents.tools.tool_wrapper import rbac_protected
from app.agents.rbac import Permission, UserRole


class TestRBACEnforcement:
    """
    Tests to verify Bug #28 fix: RBAC Enforcement.
    
    These tests verify that the @rbac_protected decorator now properly
    enforces RBAC context and raises exceptions when it's missing.
    """
    
    @pytest.mark.security
    def test_tool_raises_error_without_user_id(self):
        """
        Test that a tool raises ValueError when called without requesting_user_id.
        """
        @rbac_protected(required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value)
        def sensitive_tool(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Accessed patient {patient_id}"
        
        # Call without requesting_user_id - should raise ValueError!
        with pytest.raises(ValueError, match="RBAC violation.*requesting_user_id"):
            sensitive_tool(patient_id="123", requesting_user_role="doctor")
    
    @pytest.mark.security
    def test_tool_raises_error_without_user_role(self):
        """
        Test that a tool raises ValueError when called without requesting_user_role.
        """
        @rbac_protected(required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value)
        def sensitive_tool(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Accessed patient {patient_id}"
        
        # Call without requesting_user_role - should raise ValueError!
        with pytest.raises(ValueError, match="RBAC violation.*requesting_user_role"):
            sensitive_tool(patient_id="123", requesting_user_id="user_456")
    
    @pytest.mark.security
    def test_tool_raises_error_without_any_rbac_context(self):
        """
        Test that a tool raises ValueError when called without any RBAC context.
        """
        @rbac_protected(required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value)
        def sensitive_tool(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Accessed patient {patient_id}"
        
        # Call without any RBAC context - should raise ValueError!
        with pytest.raises(ValueError, match="RBAC violation"):
            sensitive_tool(patient_id="123")
    
    @pytest.mark.security
    def test_tool_works_with_valid_rbac_context(self):
        """
        Test that a tool works normally when called with valid RBAC context.
        """
        @rbac_protected(required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value)
        def sensitive_tool(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Accessed patient {patient_id}"
        
        # Call with valid RBAC context - should work!
        result = sensitive_tool(
            patient_id="123",
            requesting_user_id="doctor_456",
            requesting_user_role=UserRole.DOCTOR.value
        )
        
        assert result == "Accessed patient 123"
    
    @pytest.mark.security
    def test_tool_blocks_unauthorized_role(self):
        """
        Test that a tool blocks access for users without required permission.
        """
        @rbac_protected(required_permission=Permission.MANAGE_STAFF.value)
        def admin_tool(setting: str, value: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Changed {setting} to {value}"
        
        # Patient tries to call admin tool - should be blocked!
        result = admin_tool(
            setting="clinic_name",
            value="Test",
            requesting_user_id="patient_123",
            requesting_user_role=UserRole.PATIENT.value
        )
        
        # Should return permission denied message, not execute the tool
        assert "permission" in result.lower() or "denied" in result.lower()
    
    @pytest.mark.security
    def test_tool_allows_authorized_role(self):
        """
        Test that a tool allows access for users with required permission.
        """
        @rbac_protected(required_permission=Permission.MANAGE_STAFF.value)
        def admin_tool(setting: str, value: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Changed {setting} to {value}"
        
        # Clinic admin calls admin tool - should work!
        result = admin_tool(
            setting="clinic_name",
            value="Test Clinic",
            requesting_user_id="admin_123",
            requesting_user_role=UserRole.CLINIC_ADMIN.value
        )
        
        assert result == "Changed clinic_name to Test Clinic"
    
    @pytest.mark.security
    def test_tool_allows_self_access(self):
        """
        Test that a tool allows users to access their own resources.
        """
        @rbac_protected(
            required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value,
            resource_type="patient",
            allow_self_access=True
        )
        def get_patient_data(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Patient {patient_id} medical records"
        
        # Patient accessing their own data - should work!
        result = get_patient_data(
            patient_id="patient_123",
            requesting_user_id="patient_123",
            requesting_user_role=UserRole.PATIENT.value
        )
        
        assert result == "Patient patient_123 medical records"
    
    @pytest.mark.security
    def test_tool_blocks_cross_patient_access(self):
        """
        Test that a tool blocks patients from accessing other patients' data.
        """
        @rbac_protected(
            required_permission=Permission.READ_PATIENT_MEDICAL_RECORDS.value,
            resource_type="patient",
            allow_self_access=True
        )
        def get_patient_data(patient_id: str, requesting_user_id: str = None, requesting_user_role: str = None):
            return f"Patient {patient_id} medical records"
        
        # Patient 1 tries to access Patient 2's data - should be blocked!
        result = get_patient_data(
            patient_id="patient_2",
            requesting_user_id="patient_1",
            requesting_user_role=UserRole.PATIENT.value
        )
        
        # Should return permission denied message
        assert "permission" in result.lower() or "denied" in result.lower()

