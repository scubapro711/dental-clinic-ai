import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  ROLES,
  WIDGET_PERMISSIONS,
  FEATURE_PERMISSIONS,
  hasRolePermission,
  canViewWidget,
  canInteractWithWidget,
  hasFeaturePermission,
  getUserRole,
  getUserInfo,
  isAdmin,
  isStaff,
  isPatient,
  getVisibleWidgets,
  getInteractiveWidgets,
  getAvailableFeatures,
  formatRoleName,
  getRoleBadgeColor,
} from './rbac.js';

describe('RBAC Utilities', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('ROLES constant', () => {
    it('should have all required role constants', () => {
      expect(ROLES).toHaveProperty('SUPER_ADMIN');
      expect(ROLES).toHaveProperty('ORG_ADMIN');
      expect(ROLES).toHaveProperty('ORG_STAFF');
      expect(ROLES).toHaveProperty('ORG_VIEWER');
    });

    it('should have correct role values', () => {
      expect(ROLES.SUPER_ADMIN).toBe('super_admin');
      expect(ROLES.ORG_ADMIN).toBe('org_admin');
      expect(ROLES.ORG_STAFF).toBe('org_staff');
      expect(ROLES.ORG_VIEWER).toBe('org_viewer');
    });
  });

  describe('hasRolePermission', () => {
    it('should return true when user role equals required role', () => {
      expect(hasRolePermission(ROLES.ORG_ADMIN, ROLES.ORG_ADMIN)).toBe(true);
      expect(hasRolePermission(ROLES.ORG_STAFF, ROLES.ORG_STAFF)).toBe(true);
      expect(hasRolePermission(ROLES.ORG_VIEWER, ROLES.ORG_VIEWER)).toBe(true);
    });

    it('should return true when user role is higher than required role', () => {
      expect(hasRolePermission(ROLES.SUPER_ADMIN, ROLES.ORG_ADMIN)).toBe(true);
      expect(hasRolePermission(ROLES.SUPER_ADMIN, ROLES.ORG_STAFF)).toBe(true);
      expect(hasRolePermission(ROLES.SUPER_ADMIN, ROLES.ORG_VIEWER)).toBe(true);
      expect(hasRolePermission(ROLES.ORG_ADMIN, ROLES.ORG_STAFF)).toBe(true);
      expect(hasRolePermission(ROLES.ORG_ADMIN, ROLES.ORG_VIEWER)).toBe(true);
      expect(hasRolePermission(ROLES.ORG_STAFF, ROLES.ORG_VIEWER)).toBe(true);
    });

    it('should return false when user role is lower than required role', () => {
      expect(hasRolePermission(ROLES.ORG_VIEWER, ROLES.ORG_STAFF)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_VIEWER, ROLES.ORG_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_VIEWER, ROLES.SUPER_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_STAFF, ROLES.ORG_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_STAFF, ROLES.SUPER_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_ADMIN, ROLES.SUPER_ADMIN)).toBe(false);
    });

    it('should return false for invalid roles', () => {
      expect(hasRolePermission('invalid_role', ROLES.ORG_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_ADMIN, 'invalid_role')).toBe(false);
      expect(hasRolePermission('invalid_role', 'invalid_role')).toBe(false);
    });

    it('should return false for null or undefined roles', () => {
      expect(hasRolePermission(null, ROLES.ORG_ADMIN)).toBe(false);
      expect(hasRolePermission(undefined, ROLES.ORG_ADMIN)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_ADMIN, null)).toBe(false);
      expect(hasRolePermission(ROLES.ORG_ADMIN, undefined)).toBe(false);
    });
  });

  describe('canViewWidget', () => {
    it('should allow org_admin to view admin-only widgets', () => {
      expect(canViewWidget(ROLES.ORG_ADMIN, 'fine-tuning')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'revenue')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'analytics')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'settings')).toBe(true);
    });

    it('should allow org_admin and org_staff to view staff widgets', () => {
      expect(canViewWidget(ROLES.ORG_ADMIN, 'todays-patients')).toBe(true);
      expect(canViewWidget(ROLES.ORG_STAFF, 'todays-patients')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'decision-queue')).toBe(true);
      expect(canViewWidget(ROLES.ORG_STAFF, 'decision-queue')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'agent-activity')).toBe(true);
      expect(canViewWidget(ROLES.ORG_STAFF, 'agent-activity')).toBe(true);
    });

    it('should not allow org_viewer to view admin/staff widgets', () => {
      expect(canViewWidget(ROLES.ORG_VIEWER, 'fine-tuning')).toBe(false);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'revenue')).toBe(false);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'todays-patients')).toBe(false);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'decision-queue')).toBe(false);
    });

    it('should allow org_viewer to view patient widgets', () => {
      expect(canViewWidget(ROLES.ORG_VIEWER, 'patient-dashboard')).toBe(true);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'patient-appointments')).toBe(true);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'patient-medical-records')).toBe(true);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'patient-billing')).toBe(true);
    });

    it('should allow all roles to view ai-chat widget', () => {
      expect(canViewWidget(ROLES.SUPER_ADMIN, 'ai-chat')).toBe(true);
      expect(canViewWidget(ROLES.ORG_ADMIN, 'ai-chat')).toBe(true);
      expect(canViewWidget(ROLES.ORG_STAFF, 'ai-chat')).toBe(true);
      expect(canViewWidget(ROLES.ORG_VIEWER, 'ai-chat')).toBe(true);
    });

    it('should return false for non-existent widgets', () => {
      expect(canViewWidget(ROLES.ORG_ADMIN, 'non-existent-widget')).toBe(false);
      expect(canViewWidget(ROLES.ORG_STAFF, 'invalid-widget')).toBe(false);
    });

    it('should return false for invalid roles', () => {
      expect(canViewWidget('invalid_role', 'fine-tuning')).toBe(false);
      expect(canViewWidget(null, 'fine-tuning')).toBe(false);
      expect(canViewWidget(undefined, 'fine-tuning')).toBe(false);
    });

    it('should handle super_admin with hierarchy correctly', () => {
      // super_admin should see everything admin and staff can see
      expect(canViewWidget(ROLES.SUPER_ADMIN, 'fine-tuning')).toBe(true);
      expect(canViewWidget(ROLES.SUPER_ADMIN, 'todays-patients')).toBe(true);
      expect(canViewWidget(ROLES.SUPER_ADMIN, 'decision-queue')).toBe(true);
    });
  });

  describe('canInteractWithWidget', () => {
    it('should allow org_admin to interact with admin-only widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_ADMIN, 'fine-tuning')).toBe(true);
      expect(canInteractWithWidget(ROLES.ORG_ADMIN, 'revenue')).toBe(true);
      expect(canInteractWithWidget(ROLES.ORG_ADMIN, 'decision-queue')).toBe(true);
    });

    it('should not allow org_staff to interact with admin-only widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_STAFF, 'fine-tuning')).toBe(false);
      expect(canInteractWithWidget(ROLES.ORG_STAFF, 'revenue')).toBe(false);
      expect(canInteractWithWidget(ROLES.ORG_STAFF, 'decision-queue')).toBe(false);
    });

    it('should allow org_staff to interact with staff widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_STAFF, 'todays-patients')).toBe(true);
      expect(canInteractWithWidget(ROLES.ORG_STAFF, 'agent-activity')).toBe(true);
    });

    it('should not allow org_viewer to interact with admin/staff widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_VIEWER, 'fine-tuning')).toBe(false);
      expect(canInteractWithWidget(ROLES.ORG_VIEWER, 'todays-patients')).toBe(false);
      expect(canInteractWithWidget(ROLES.ORG_VIEWER, 'decision-queue')).toBe(false);
    });

    it('should allow org_viewer to interact with patient widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_VIEWER, 'patient-dashboard')).toBe(true);
      expect(canInteractWithWidget(ROLES.ORG_VIEWER, 'patient-appointments')).toBe(true);
    });

    it('should return false for non-existent widgets', () => {
      expect(canInteractWithWidget(ROLES.ORG_ADMIN, 'non-existent')).toBe(false);
    });

    it('should handle super_admin with hierarchy correctly', () => {
      expect(canInteractWithWidget(ROLES.SUPER_ADMIN, 'fine-tuning')).toBe(true);
      expect(canInteractWithWidget(ROLES.SUPER_ADMIN, 'decision-queue')).toBe(true);
    });
  });

  describe('hasFeaturePermission', () => {
    it('should allow org_admin to approve/reject suggestions', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'approve-suggestions')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'reject-suggestions')).toBe(true);
    });

    it('should not allow org_staff to approve/reject suggestions', () => {
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'approve-suggestions')).toBe(false);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'reject-suggestions')).toBe(false);
    });

    it('should allow org_admin and org_staff to provide feedback', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'provide-feedback')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'provide-feedback')).toBe(true);
    });

    it('should allow org_admin to fine-tune models', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'fine-tune-models')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'fine-tune-models')).toBe(false);
    });

    it('should allow org_admin and org_staff to create/edit patients', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'create-patient')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'create-patient')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'edit-patient')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'edit-patient')).toBe(true);
    });

    it('should only allow org_admin to delete patients', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'delete-patient')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'delete-patient')).toBe(false);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'delete-patient')).toBe(false);
    });

    it('should allow all roles to create appointments', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'create-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'create-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'create-appointment')).toBe(true);
    });

    it('should only allow admin/staff to edit appointments', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'edit-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'edit-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'edit-appointment')).toBe(false);
    });

    it('should allow all roles to cancel appointments', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'cancel-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'cancel-appointment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'cancel-appointment')).toBe(true);
    });

    it('should only allow org_admin to view revenue', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'view-revenue')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'view-revenue')).toBe(false);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'view-revenue')).toBe(false);
    });

    it('should allow all roles to view billing', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'view-billing')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'view-billing')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'view-billing')).toBe(true);
    });

    it('should only allow admin/staff to process payments', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'process-payment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'process-payment')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'process-payment')).toBe(false);
    });

    it('should allow all roles to view medical records', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'view-medical-records')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'view-medical-records')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'view-medical-records')).toBe(true);
    });

    it('should only allow admin/staff to edit medical records', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'edit-medical-records')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'edit-medical-records')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_VIEWER, 'edit-medical-records')).toBe(false);
    });

    it('should only allow org_admin to view analytics and manage settings', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'view-analytics')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'manage-settings')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'manage-users')).toBe(true);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'view-analytics')).toBe(false);
      expect(hasFeaturePermission(ROLES.ORG_STAFF, 'manage-settings')).toBe(false);
    });

    it('should return false for non-existent features', () => {
      expect(hasFeaturePermission(ROLES.ORG_ADMIN, 'non-existent-feature')).toBe(false);
    });

    it('should handle super_admin with hierarchy correctly', () => {
      expect(hasFeaturePermission(ROLES.SUPER_ADMIN, 'approve-suggestions')).toBe(true);
      expect(hasFeaturePermission(ROLES.SUPER_ADMIN, 'delete-patient')).toBe(true);
      expect(hasFeaturePermission(ROLES.SUPER_ADMIN, 'manage-users')).toBe(true);
    });
  });

  describe('getUserRole', () => {
    it('should return role from localStorage mockUser', () => {
      const mockUser = { role: ROLES.ORG_ADMIN, email: 'admin@test.com' };
      localStorage.setItem('mockUser', JSON.stringify(mockUser));
      
      expect(getUserRole()).toBe(ROLES.ORG_ADMIN);
    });

    it('should return ORG_VIEWER as default when no mockUser', () => {
      expect(getUserRole()).toBe(ROLES.ORG_VIEWER);
    });

    it('should return ORG_VIEWER when mockUser is invalid JSON', () => {
      localStorage.setItem('mockUser', 'invalid json');
      expect(getUserRole()).toBe(ROLES.ORG_VIEWER);
    });

    it('should handle different roles correctly', () => {
      const roles = [ROLES.SUPER_ADMIN, ROLES.ORG_ADMIN, ROLES.ORG_STAFF, ROLES.ORG_VIEWER];
      
      roles.forEach(role => {
        localStorage.setItem('mockUser', JSON.stringify({ role }));
        expect(getUserRole()).toBe(role);
      });
    });
  });

  describe('getUserInfo', () => {
    it('should return user info from localStorage mockUser', () => {
      const mockUser = {
        role: ROLES.ORG_ADMIN,
        email: 'admin@test.com',
        name: 'Admin User',
      };
      localStorage.setItem('mockUser', JSON.stringify(mockUser));
      
      const userInfo = getUserInfo();
      expect(userInfo).toEqual(mockUser);
    });

    it('should return default guest user when no mockUser', () => {
      const userInfo = getUserInfo();
      expect(userInfo).toEqual({
        email: 'guest@dentaflow.ai',
        role: ROLES.ORG_VIEWER,
        name: 'Guest User',
      });
    });

    it('should return default guest user when mockUser is invalid JSON', () => {
      localStorage.setItem('mockUser', 'invalid json');
      const userInfo = getUserInfo();
      expect(userInfo).toEqual({
        email: 'guest@dentaflow.ai',
        role: ROLES.ORG_VIEWER,
        name: 'Guest User',
      });
    });
  });

  describe('isAdmin', () => {
    it('should return true for org_admin', () => {
      expect(isAdmin(ROLES.ORG_ADMIN)).toBe(true);
    });

    it('should return true for super_admin', () => {
      expect(isAdmin(ROLES.SUPER_ADMIN)).toBe(true);
    });

    it('should return false for org_staff', () => {
      expect(isAdmin(ROLES.ORG_STAFF)).toBe(false);
    });

    it('should return false for org_viewer', () => {
      expect(isAdmin(ROLES.ORG_VIEWER)).toBe(false);
    });

    it('should return false for invalid roles', () => {
      expect(isAdmin('invalid_role')).toBe(false);
      expect(isAdmin(null)).toBe(false);
      expect(isAdmin(undefined)).toBe(false);
    });
  });

  describe('isStaff', () => {
    it('should return true for org_staff', () => {
      expect(isStaff(ROLES.ORG_STAFF)).toBe(true);
    });

    it('should return true for org_admin (higher role)', () => {
      expect(isStaff(ROLES.ORG_ADMIN)).toBe(true);
    });

    it('should return true for super_admin (higher role)', () => {
      expect(isStaff(ROLES.SUPER_ADMIN)).toBe(true);
    });

    it('should return false for org_viewer', () => {
      expect(isStaff(ROLES.ORG_VIEWER)).toBe(false);
    });

    it('should return false for invalid roles', () => {
      expect(isStaff('invalid_role')).toBe(false);
      expect(isStaff(null)).toBe(false);
      expect(isStaff(undefined)).toBe(false);
    });
  });

  describe('isPatient', () => {
    it('should return true for org_viewer', () => {
      expect(isPatient(ROLES.ORG_VIEWER)).toBe(true);
    });

    it('should return false for org_staff', () => {
      expect(isPatient(ROLES.ORG_STAFF)).toBe(false);
    });

    it('should return false for org_admin', () => {
      expect(isPatient(ROLES.ORG_ADMIN)).toBe(false);
    });

    it('should return false for super_admin', () => {
      expect(isPatient(ROLES.SUPER_ADMIN)).toBe(false);
    });

    it('should return false for invalid roles', () => {
      expect(isPatient('invalid_role')).toBe(false);
      expect(isPatient(null)).toBe(false);
      expect(isPatient(undefined)).toBe(false);
    });
  });

  describe('getVisibleWidgets', () => {
    it('should return all admin widgets for org_admin', () => {
      const widgets = getVisibleWidgets(ROLES.ORG_ADMIN);
      expect(widgets).toContain('fine-tuning');
      expect(widgets).toContain('revenue');
      expect(widgets).toContain('todays-patients');
      expect(widgets).toContain('decision-queue');
      expect(widgets).toContain('analytics');
      expect(widgets).toContain('settings');
    });

    it('should return staff widgets for org_staff', () => {
      const widgets = getVisibleWidgets(ROLES.ORG_STAFF);
      expect(widgets).toContain('todays-patients');
      expect(widgets).toContain('decision-queue');
      expect(widgets).toContain('agent-activity');
      expect(widgets).not.toContain('fine-tuning');
      expect(widgets).not.toContain('revenue');
    });

    it('should return patient widgets for org_viewer', () => {
      const widgets = getVisibleWidgets(ROLES.ORG_VIEWER);
      expect(widgets).toContain('patient-dashboard');
      expect(widgets).toContain('patient-appointments');
      expect(widgets).toContain('patient-medical-records');
      expect(widgets).toContain('patient-billing');
      expect(widgets).not.toContain('fine-tuning');
      expect(widgets).not.toContain('todays-patients');
    });

    it('should return ai-chat for all roles', () => {
      expect(getVisibleWidgets(ROLES.ORG_ADMIN)).toContain('ai-chat');
      expect(getVisibleWidgets(ROLES.ORG_STAFF)).toContain('ai-chat');
      expect(getVisibleWidgets(ROLES.ORG_VIEWER)).toContain('ai-chat');
    });

    it('should return empty array for invalid role', () => {
      const widgets = getVisibleWidgets('invalid_role');
      expect(widgets).toEqual([]);
    });
  });

  describe('getInteractiveWidgets', () => {
    it('should return all interactive widgets for org_admin', () => {
      const widgets = getInteractiveWidgets(ROLES.ORG_ADMIN);
      expect(widgets).toContain('fine-tuning');
      expect(widgets).toContain('revenue');
      expect(widgets).toContain('decision-queue');
    });

    it('should not include decision-queue for org_staff', () => {
      const widgets = getInteractiveWidgets(ROLES.ORG_STAFF);
      expect(widgets).toContain('todays-patients');
      expect(widgets).not.toContain('decision-queue');
      expect(widgets).not.toContain('fine-tuning');
    });

    it('should return patient interactive widgets for org_viewer', () => {
      const widgets = getInteractiveWidgets(ROLES.ORG_VIEWER);
      expect(widgets).toContain('patient-dashboard');
      expect(widgets).toContain('patient-appointments');
      expect(widgets).not.toContain('todays-patients');
    });
  });

  describe('getAvailableFeatures', () => {
    it('should return all features for org_admin', () => {
      const features = getAvailableFeatures(ROLES.ORG_ADMIN);
      expect(features).toContain('approve-suggestions');
      expect(features).toContain('reject-suggestions');
      expect(features).toContain('fine-tune-models');
      expect(features).toContain('delete-patient');
      expect(features).toContain('view-revenue');
      expect(features).toContain('manage-settings');
    });

    it('should return limited features for org_staff', () => {
      const features = getAvailableFeatures(ROLES.ORG_STAFF);
      expect(features).toContain('provide-feedback');
      expect(features).toContain('create-patient');
      expect(features).toContain('edit-appointment');
      expect(features).not.toContain('approve-suggestions');
      expect(features).not.toContain('fine-tune-models');
      expect(features).not.toContain('delete-patient');
    });

    it('should return basic features for org_viewer', () => {
      const features = getAvailableFeatures(ROLES.ORG_VIEWER);
      expect(features).toContain('create-appointment');
      expect(features).toContain('cancel-appointment');
      expect(features).toContain('view-billing');
      expect(features).toContain('view-medical-records');
      expect(features).not.toContain('edit-patient');
      expect(features).not.toContain('approve-suggestions');
    });
  });

  describe('formatRoleName', () => {
    it('should format super_admin correctly', () => {
      expect(formatRoleName(ROLES.SUPER_ADMIN)).toBe('Super Admin');
    });

    it('should format org_admin correctly', () => {
      expect(formatRoleName(ROLES.ORG_ADMIN)).toBe('Organization Admin');
    });

    it('should format org_staff correctly', () => {
      expect(formatRoleName(ROLES.ORG_STAFF)).toBe('Staff Member');
    });

    it('should format org_viewer correctly', () => {
      expect(formatRoleName(ROLES.ORG_VIEWER)).toBe('Patient');
    });

    it('should return original role for unknown roles', () => {
      expect(formatRoleName('unknown_role')).toBe('unknown_role');
    });

    it('should handle null and undefined', () => {
      expect(formatRoleName(null)).toBe(null);
      expect(formatRoleName(undefined)).toBe(undefined);
    });
  });

  describe('getRoleBadgeColor', () => {
    it('should return red for super_admin', () => {
      expect(getRoleBadgeColor(ROLES.SUPER_ADMIN)).toBe('bg-red-500');
    });

    it('should return blue for org_admin', () => {
      expect(getRoleBadgeColor(ROLES.ORG_ADMIN)).toBe('bg-blue-500');
    });

    it('should return green for org_staff', () => {
      expect(getRoleBadgeColor(ROLES.ORG_STAFF)).toBe('bg-green-500');
    });

    it('should return gray for org_viewer', () => {
      expect(getRoleBadgeColor(ROLES.ORG_VIEWER)).toBe('bg-gray-500');
    });

    it('should return default gray for unknown roles', () => {
      expect(getRoleBadgeColor('unknown_role')).toBe('bg-gray-500');
    });

    it('should return default gray for null and undefined', () => {
      expect(getRoleBadgeColor(null)).toBe('bg-gray-500');
      expect(getRoleBadgeColor(undefined)).toBe('bg-gray-500');
    });
  });

  describe('WIDGET_PERMISSIONS constant', () => {
    it('should have all required widgets defined', () => {
      const requiredWidgets = [
        'todays-patients',
        'decision-queue',
        'fine-tuning',
        'revenue',
        'agent-activity',
        'transparency-panel',
        'ai-chat',
        'patient-dashboard',
        'patient-appointments',
        'patient-medical-records',
        'patient-billing',
        'patients-management',
        'appointments-management',
        'analytics',
        'settings',
      ];

      requiredWidgets.forEach(widget => {
        expect(WIDGET_PERMISSIONS).toHaveProperty(widget);
        expect(WIDGET_PERMISSIONS[widget]).toHaveProperty('view');
        expect(WIDGET_PERMISSIONS[widget]).toHaveProperty('interact');
      });
    });
  });

  describe('FEATURE_PERMISSIONS constant', () => {
    it('should have all required features defined', () => {
      const requiredFeatures = [
        'approve-suggestions',
        'reject-suggestions',
        'provide-feedback',
        'fine-tune-models',
        'view-agent-reasoning',
        'create-patient',
        'edit-patient',
        'delete-patient',
        'view-patient-list',
        'create-appointment',
        'edit-appointment',
        'cancel-appointment',
        'view-revenue',
        'view-billing',
        'process-payment',
        'view-medical-records',
        'edit-medical-records',
        'upload-xray',
        'sarah-analysis',
        'view-analytics',
        'manage-settings',
        'manage-users',
      ];

      requiredFeatures.forEach(feature => {
        expect(FEATURE_PERMISSIONS).toHaveProperty(feature);
        expect(Array.isArray(FEATURE_PERMISSIONS[feature])).toBe(true);
      });
    });
  });
});

