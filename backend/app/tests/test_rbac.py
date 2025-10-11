"""
Comprehensive tests for RBAC (Role-Based Access Control) module.

Tests cover:
- Role hierarchy
- Role permission checking
- require_role decorator
- require_roles decorator
- require_ownership decorator
- check_resource_ownership function
- Edge cases and error handling
"""

import pytest
from fastapi import HTTPException
from unittest.mock import Mock, AsyncMock
from app.core.rbac import (
    Role,
    require_role,
    require_roles,
    require_ownership,
    check_resource_ownership,
)
from app.models.user import User


# Test Role class and hierarchy
class TestRole:
    """Tests for Role class and role hierarchy."""
    
    def test_role_constants(self):
        """Test that all role constants are defined."""
        assert Role.ADMIN == "admin"
        assert Role.OWNER == "owner"
        assert Role.STAFF == "staff"
        assert Role.PATIENT == "patient"
    
    def test_role_hierarchy_values(self):
        """Test that role hierarchy has correct values."""
        assert Role.HIERARCHY[Role.ADMIN] == 4
        assert Role.HIERARCHY[Role.OWNER] == 3
        assert Role.HIERARCHY[Role.STAFF] == 2
        assert Role.HIERARCHY[Role.PATIENT] == 1
    
    def test_has_permission_same_role(self):
        """Test permission check when user has exact required role."""
        assert Role.has_permission(Role.ADMIN, Role.ADMIN) is True
        assert Role.has_permission(Role.OWNER, Role.OWNER) is True
        assert Role.has_permission(Role.STAFF, Role.STAFF) is True
        assert Role.has_permission(Role.PATIENT, Role.PATIENT) is True
    
    def test_has_permission_higher_role(self):
        """Test permission check when user has higher role."""
        # Admin can do everything
        assert Role.has_permission(Role.ADMIN, Role.OWNER) is True
        assert Role.has_permission(Role.ADMIN, Role.STAFF) is True
        assert Role.has_permission(Role.ADMIN, Role.PATIENT) is True
        
        # Owner can do staff and patient tasks
        assert Role.has_permission(Role.OWNER, Role.STAFF) is True
        assert Role.has_permission(Role.OWNER, Role.PATIENT) is True
        
        # Staff can do patient tasks
        assert Role.has_permission(Role.STAFF, Role.PATIENT) is True
    
    def test_has_permission_lower_role(self):
        """Test permission check when user has lower role."""
        # Patient cannot do staff tasks
        assert Role.has_permission(Role.PATIENT, Role.STAFF) is False
        assert Role.has_permission(Role.PATIENT, Role.OWNER) is False
        assert Role.has_permission(Role.PATIENT, Role.ADMIN) is False
        
        # Staff cannot do owner/admin tasks
        assert Role.has_permission(Role.STAFF, Role.OWNER) is False
        assert Role.has_permission(Role.STAFF, Role.ADMIN) is False
        
        # Owner cannot do admin tasks
        assert Role.has_permission(Role.OWNER, Role.ADMIN) is False
    
    def test_has_permission_invalid_role(self):
        """Test permission check with invalid roles."""
        assert Role.has_permission("invalid_role", Role.ADMIN) is False
        assert Role.has_permission(Role.ADMIN, "invalid_role") is False
        assert Role.has_permission("invalid_role", "invalid_role") is False
    
    def test_has_permission_none_role(self):
        """Test permission check with None roles."""
        assert Role.has_permission(None, Role.ADMIN) is False
        assert Role.has_permission(Role.ADMIN, None) is False
        assert Role.has_permission(None, None) is False


# Test require_role decorator
class TestRequireRoleDecorator:
    """Tests for require_role decorator."""
    
    @pytest.mark.asyncio
    async def test_require_role_with_permission(self):
        """Test that user with required role can access endpoint."""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with admin role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.ADMIN
        
        result = await test_endpoint(current_user=mock_user)
        assert result == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_require_role_with_higher_role(self):
        """Test that user with higher role can access endpoint."""
        @require_role(Role.STAFF)
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with admin role (higher than staff)
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.ADMIN
        
        result = await test_endpoint(current_user=mock_user)
        assert result == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_require_role_without_permission(self):
        """Test that user without required role cannot access endpoint."""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with patient role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.PATIENT
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user)
        
        assert exc_info.value.status_code == 403
        assert "admin role required" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_role_no_user(self):
        """Test that endpoint raises error when no user provided."""
        @require_role(Role.ADMIN)
        async def test_endpoint():
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint()
        
        assert exc_info.value.status_code == 500
        assert "authentication failed" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_role_user_without_role(self):
        """Test that endpoint raises error when user has no role."""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user without role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = None
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user)
        
        assert exc_info.value.status_code == 403
        assert "no role assigned" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_role_with_positional_user(self):
        """Test that decorator works with user as positional argument."""
        @require_role(Role.ADMIN)
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with admin role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.ADMIN
        
        result = await test_endpoint(mock_user)
        assert result == {"message": "success"}


# Test require_roles decorator
class TestRequireRolesDecorator:
    """Tests for require_roles decorator."""
    
    @pytest.mark.asyncio
    async def test_require_roles_with_one_matching_role(self):
        """Test that user with one of required roles can access endpoint."""
        @require_roles([Role.ADMIN, Role.OWNER])
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with owner role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.OWNER
        
        result = await test_endpoint(current_user=mock_user)
        assert result == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_require_roles_with_higher_role(self):
        """Test that user with higher role can access endpoint."""
        @require_roles([Role.STAFF, Role.OWNER])
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with admin role (higher than both)
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.ADMIN
        
        result = await test_endpoint(current_user=mock_user)
        assert result == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_require_roles_without_permission(self):
        """Test that user without any required role cannot access endpoint."""
        @require_roles([Role.ADMIN, Role.OWNER])
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with patient role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.PATIENT
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user)
        
        assert exc_info.value.status_code == 403
        assert "one of" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_roles_staff_can_access_staff_endpoint(self):
        """Test that staff can access staff-level endpoints."""
        @require_roles([Role.ADMIN, Role.OWNER, Role.STAFF])
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with staff role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.STAFF
        
        result = await test_endpoint(current_user=mock_user)
        assert result == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_require_roles_empty_list(self):
        """Test behavior with empty required roles list."""
        @require_roles([])
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        # Create mock user with patient role
        mock_user = Mock(spec=User)
        mock_user.id = "test-user-id"
        mock_user.role = Role.PATIENT
        
        # Empty list means no roles required, should deny access
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=mock_user)
        
        assert exc_info.value.status_code == 403


# Test check_resource_ownership function
class TestCheckResourceOwnership:
    """Tests for check_resource_ownership function."""
    
    def test_admin_can_access_any_resource(self):
        """Test that admin can access any resource."""
        admin_user = Mock(spec=User)
        admin_user.id = "admin-id"
        admin_user.role = Role.ADMIN
        
        assert check_resource_ownership(admin_user, "other-user-id") is True
    
    def test_owner_can_access_any_resource(self):
        """Test that owner can access any resource."""
        owner_user = Mock(spec=User)
        owner_user.id = "owner-id"
        owner_user.role = Role.OWNER
        
        assert check_resource_ownership(owner_user, "other-user-id") is True
    
    def test_user_can_access_own_resource(self):
        """Test that user can access their own resource."""
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        assert check_resource_ownership(user, "user-id") is True
    
    def test_user_cannot_access_others_resource(self):
        """Test that user cannot access other user's resource."""
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        assert check_resource_ownership(user, "other-user-id") is False
    
    def test_patient_can_access_own_resource(self):
        """Test that patient can access their own resource."""
        patient = Mock(spec=User)
        patient.id = "patient-id"
        patient.role = Role.PATIENT
        
        assert check_resource_ownership(patient, "patient-id") is True
    
    def test_patient_cannot_access_others_resource(self):
        """Test that patient cannot access other user's resource."""
        patient = Mock(spec=User)
        patient.id = "patient-id"
        patient.role = Role.PATIENT
        
        assert check_resource_ownership(patient, "other-user-id") is False
    
    def test_ownership_with_string_ids(self):
        """Test ownership check with string IDs."""
        user = Mock(spec=User)
        user.id = "123"
        user.role = Role.STAFF
        
        assert check_resource_ownership(user, "123") is True
        assert check_resource_ownership(user, "456") is False


# Test require_ownership decorator
class TestRequireOwnershipDecorator:
    """Tests for require_ownership decorator."""
    
    @pytest.mark.asyncio
    async def test_require_ownership_admin_access(self):
        """Test that admin can access any resource."""
        @require_ownership("user_id")
        async def test_endpoint(user_id: str, current_user: User):
            return {"message": "success", "user_id": user_id}
        
        admin_user = Mock(spec=User)
        admin_user.id = "admin-id"
        admin_user.role = Role.ADMIN
        
        result = await test_endpoint(user_id="other-user-id", current_user=admin_user)
        assert result["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_require_ownership_own_resource(self):
        """Test that user can access their own resource."""
        @require_ownership("user_id")
        async def test_endpoint(user_id: str, current_user: User):
            return {"message": "success", "user_id": user_id}
        
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        result = await test_endpoint(user_id="user-id", current_user=user)
        assert result["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_require_ownership_others_resource(self):
        """Test that user cannot access other user's resource."""
        @require_ownership("user_id")
        async def test_endpoint(user_id: str, current_user: User):
            return {"message": "success", "user_id": user_id}
        
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(user_id="other-user-id", current_user=user)
        
        assert exc_info.value.status_code == 403
        assert "your own resources" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_ownership_missing_parameter(self):
        """Test that decorator raises error when resource ID parameter is missing."""
        @require_ownership("user_id")
        async def test_endpoint(current_user: User):
            return {"message": "success"}
        
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(current_user=user)
        
        assert exc_info.value.status_code == 400
        assert "Missing required parameter" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_require_ownership_custom_parameter_name(self):
        """Test that decorator works with custom parameter name."""
        @require_ownership("patient_id")
        async def test_endpoint(patient_id: str, current_user: User):
            return {"message": "success", "patient_id": patient_id}
        
        user = Mock(spec=User)
        user.id = "user-id"
        user.role = Role.STAFF
        
        result = await test_endpoint(patient_id="user-id", current_user=user)
        assert result["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_require_ownership_no_user(self):
        """Test that decorator raises error when no user provided."""
        @require_ownership("user_id")
        async def test_endpoint(user_id: str):
            return {"message": "success"}
        
        with pytest.raises(HTTPException) as exc_info:
            await test_endpoint(user_id="user-id")
        
        assert exc_info.value.status_code == 500
        assert "authentication failed" in exc_info.value.detail


# Integration tests
class TestRBACIntegration:
    """Integration tests for RBAC decorators."""
    
    @pytest.mark.asyncio
    async def test_multiple_decorators(self):
        """Test using multiple RBAC decorators together."""
        @require_role(Role.STAFF)
        @require_ownership("user_id")
        async def test_endpoint(user_id: str, current_user: User):
            return {"message": "success"}
        
        # Staff accessing their own resource
        staff_user = Mock(spec=User)
        staff_user.id = "staff-id"
        staff_user.role = Role.STAFF
        
        result = await test_endpoint(user_id="staff-id", current_user=staff_user)
        assert result["message"] == "success"
    
    @pytest.mark.asyncio
    async def test_role_hierarchy_in_practice(self):
        """Test that role hierarchy works correctly in practice."""
        @require_role(Role.PATIENT)
        async def patient_endpoint(current_user: User):
            return {"message": "patient endpoint"}
        
        @require_role(Role.STAFF)
        async def staff_endpoint(current_user: User):
            return {"message": "staff endpoint"}
        
        @require_role(Role.ADMIN)
        async def admin_endpoint(current_user: User):
            return {"message": "admin endpoint"}
        
        # Admin can access all endpoints
        admin_user = Mock(spec=User)
        admin_user.id = "admin-id"
        admin_user.role = Role.ADMIN
        
        assert (await patient_endpoint(current_user=admin_user))["message"] == "patient endpoint"
        assert (await staff_endpoint(current_user=admin_user))["message"] == "staff endpoint"
        assert (await admin_endpoint(current_user=admin_user))["message"] == "admin endpoint"
        
        # Staff can access patient and staff endpoints
        staff_user = Mock(spec=User)
        staff_user.id = "staff-id"
        staff_user.role = Role.STAFF
        
        assert (await patient_endpoint(current_user=staff_user))["message"] == "patient endpoint"
        assert (await staff_endpoint(current_user=staff_user))["message"] == "staff endpoint"
        
        with pytest.raises(HTTPException):
            await admin_endpoint(current_user=staff_user)
        
        # Patient can only access patient endpoints
        patient_user = Mock(spec=User)
        patient_user.id = "patient-id"
        patient_user.role = Role.PATIENT
        
        assert (await patient_endpoint(current_user=patient_user))["message"] == "patient endpoint"
        
        with pytest.raises(HTTPException):
            await staff_endpoint(current_user=patient_user)
        
        with pytest.raises(HTTPException):
            await admin_endpoint(current_user=patient_user)

