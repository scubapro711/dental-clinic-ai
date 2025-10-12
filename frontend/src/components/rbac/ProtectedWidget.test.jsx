import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import ProtectedWidget, {
  ProtectedFeature,
  useWidgetPermissions,
  useFeaturePermission,
} from './ProtectedWidget';
import { ROLES } from '@/utils/rbac';

// Helper function to set mock user in localStorage
function setMockUser(role) {
  const mockUser = {
    role,
    email: `test-${role}@dentaflow.ai`,
    name: `Test ${role}`,
  };
  localStorage.setItem('mockUser', JSON.stringify(mockUser));
}

describe('ProtectedWidget', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('Basic rendering with permissions', () => {
    it('should render children when user has view permission', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedWidget widgetId="fine-tuning">
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Fine Tuning Widget')).toBeInTheDocument();
    });

    it('should render children when user has interact permission', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedWidget widgetId="decision-queue" requireInteract={true}>
          <div>Decision Queue Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Decision Queue Widget')).toBeInTheDocument();
    });

    it('should render children for staff with staff-level widget', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedWidget widgetId="todays-patients">
          <div>Todays Patients Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Todays Patients Widget')).toBeInTheDocument();
    });

    it('should render children for patient with patient widget', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedWidget widgetId="patient-dashboard">
          <div>Patient Dashboard Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Patient Dashboard Widget')).toBeInTheDocument();
    });
  });

  describe('Access denied scenarios', () => {
    it('should show default fallback when user lacks view permission', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedWidget widgetId="fine-tuning">
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.queryByText('Fine Tuning Widget')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
      expect(screen.getByText(/This widget requires view permissions/)).toBeInTheDocument();
    });

    it('should show default fallback when user lacks interact permission', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedWidget widgetId="decision-queue" requireInteract={true}>
          <div>Decision Queue Widget</div>
        </ProtectedWidget>
      );

      expect(screen.queryByText('Decision Queue Widget')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
      expect(screen.getByText(/This widget requires interaction permissions/)).toBeInTheDocument();
    });

    it('should display user role in fallback message', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedWidget widgetId="fine-tuning">
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText(/Your role: Patient/)).toBeInTheDocument();
    });

    it('should show correct role for staff in fallback', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedWidget widgetId="fine-tuning">
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText(/Your role: Staff Member/)).toBeInTheDocument();
    });
  });

  describe('Custom fallback', () => {
    it('should render custom fallback when provided', () => {
      setMockUser(ROLES.ORG_VIEWER);

      const customFallback = <div>Custom Permission Denied</div>;

      render(
        <ProtectedWidget widgetId="fine-tuning" fallback={customFallback}>
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Custom Permission Denied')).toBeInTheDocument();
      expect(screen.queryByText('Access Restricted')).not.toBeInTheDocument();
    });

    it('should use custom fallback over default', () => {
      setMockUser(ROLES.ORG_STAFF);

      const customFallback = <div>You need admin access</div>;

      render(
        <ProtectedWidget widgetId="revenue" fallback={customFallback}>
          <div>Revenue Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('You need admin access')).toBeInTheDocument();
      expect(screen.queryByText('Access Restricted')).not.toBeInTheDocument();
    });
  });

  describe('showFallback prop', () => {
    it('should render nothing when showFallback is false', () => {
      setMockUser(ROLES.ORG_VIEWER);

      const { container } = render(
        <ProtectedWidget widgetId="fine-tuning" showFallback={false}>
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(container.firstChild).toBeNull();
    });

    it('should render default fallback when showFallback is true', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedWidget widgetId="fine-tuning" showFallback={true}>
          <div>Fine Tuning Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });
  });

  describe('requireInteract prop', () => {
    it('should check view permission when requireInteract is false', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedWidget widgetId="decision-queue" requireInteract={false}>
          <div>Decision Queue Widget</div>
        </ProtectedWidget>
      );

      // Staff can view decision-queue
      expect(screen.getByText('Decision Queue Widget')).toBeInTheDocument();
    });

    it('should check interact permission when requireInteract is true', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedWidget widgetId="decision-queue" requireInteract={true}>
          <div>Decision Queue Widget</div>
        </ProtectedWidget>
      );

      // Staff cannot interact with decision-queue (admin only)
      expect(screen.queryByText('Decision Queue Widget')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });

    it('should allow admin to interact with admin-only widgets', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedWidget widgetId="decision-queue" requireInteract={true}>
          <div>Decision Queue Widget</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Decision Queue Widget')).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('should handle non-existent widgetId', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedWidget widgetId="non-existent-widget">
          <div>Widget Content</div>
        </ProtectedWidget>
      );

      expect(screen.queryByText('Widget Content')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });

    it('should handle missing widgetId', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedWidget>
          <div>Widget Content</div>
        </ProtectedWidget>
      );

      expect(screen.queryByText('Widget Content')).not.toBeInTheDocument();
    });

    it('should handle missing user in localStorage', () => {
      // Don't set mock user - should default to org_viewer

      render(
        <ProtectedWidget widgetId="patient-dashboard">
          <div>Patient Dashboard</div>
        </ProtectedWidget>
      );

      // Default org_viewer can see patient dashboard
      expect(screen.getByText('Patient Dashboard')).toBeInTheDocument();
    });
  });

  describe('Multiple widgets with different permissions', () => {
    it('should show different results for different roles', () => {
      setMockUser(ROLES.ORG_STAFF);

      const { rerender } = render(
        <ProtectedWidget widgetId="todays-patients">
          <div>Todays Patients</div>
        </ProtectedWidget>
      );

      expect(screen.getByText('Todays Patients')).toBeInTheDocument();

      rerender(
        <ProtectedWidget widgetId="revenue">
          <div>Revenue Widget</div>
        </ProtectedWidget>
      );

      expect(screen.queryByText('Revenue Widget')).not.toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });
  });
});

describe('ProtectedFeature', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('Basic rendering with permissions', () => {
    it('should render children when user has feature permission', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedFeature featureId="approve-suggestions">
          <button>Approve</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Approve')).toBeInTheDocument();
    });

    it('should render children for staff with staff-level feature', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedFeature featureId="provide-feedback">
          <button>Provide Feedback</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Provide Feedback')).toBeInTheDocument();
    });

    it('should render children for viewer with viewer-level feature', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedFeature featureId="create-appointment">
          <button>Create Appointment</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Create Appointment')).toBeInTheDocument();
    });
  });

  describe('Access denied scenarios', () => {
    it('should render nothing by default when user lacks permission', () => {
      setMockUser(ROLES.ORG_STAFF);

      const { container } = render(
        <ProtectedFeature featureId="approve-suggestions">
          <button>Approve</button>
        </ProtectedFeature>
      );

      expect(screen.queryByText('Approve')).not.toBeInTheDocument();
      expect(container.firstChild).toBeNull();
    });

    it('should show fallback message when showFallback is true', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedFeature featureId="approve-suggestions" showFallback={true}>
          <button>Approve</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Permission required')).toBeInTheDocument();
    });

    it('should not show fallback when showFallback is false', () => {
      setMockUser(ROLES.ORG_VIEWER);

      const { container } = render(
        <ProtectedFeature featureId="delete-patient" showFallback={false}>
          <button>Delete</button>
        </ProtectedFeature>
      );

      expect(container.firstChild).toBeNull();
    });
  });

  describe('disableInstead prop', () => {
    it('should render disabled button when disableInstead is true', () => {
      setMockUser(ROLES.ORG_STAFF);

      render(
        <ProtectedFeature featureId="approve-suggestions" disableInstead={true}>
          <button>Approve</button>
        </ProtectedFeature>
      );

      const button = screen.getByText('Approve');
      expect(button).toBeInTheDocument();
      expect(button).toBeDisabled();
    });

    it('should render enabled button when user has permission', () => {
      setMockUser(ROLES.ORG_ADMIN);

      render(
        <ProtectedFeature featureId="approve-suggestions" disableInstead={true}>
          <button>Approve</button>
        </ProtectedFeature>
      );

      const button = screen.getByText('Approve');
      expect(button).toBeInTheDocument();
      expect(button).not.toBeDisabled();
    });

    it('should work with disableInstead for different roles', () => {
      setMockUser(ROLES.ORG_VIEWER);

      render(
        <ProtectedFeature featureId="edit-patient" disableInstead={true}>
          <button>Edit Patient</button>
        </ProtectedFeature>
      );

      const button = screen.getByText('Edit Patient');
      expect(button).toBeDisabled();
    });
  });

  describe('Custom fallback', () => {
    it('should render custom fallback when provided', () => {
      setMockUser(ROLES.ORG_STAFF);

      const customFallback = <div>Custom Feature Denied</div>;

      render(
        <ProtectedFeature featureId="approve-suggestions" fallback={customFallback}>
          <button>Approve</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Custom Feature Denied')).toBeInTheDocument();
      expect(screen.queryByText('Approve')).not.toBeInTheDocument();
    });
  });

  describe('Multiple features with different permissions', () => {
    it('should handle multiple features correctly', () => {
      setMockUser(ROLES.ORG_STAFF);

      const { rerender } = render(
        <ProtectedFeature featureId="provide-feedback">
          <button>Provide Feedback</button>
        </ProtectedFeature>
      );

      expect(screen.getByText('Provide Feedback')).toBeInTheDocument();

      rerender(
        <ProtectedFeature featureId="fine-tune-models">
          <button>Fine-tune</button>
        </ProtectedFeature>
      );

      expect(screen.queryByText('Fine-tune')).not.toBeInTheDocument();
    });
  });
});

describe('useWidgetPermissions hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return correct permissions for admin', () => {
    setMockUser(ROLES.ORG_ADMIN);

    let hookResult;
    function TestComponent() {
      hookResult = useWidgetPermissions('fine-tuning');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.canView).toBe(true);
    expect(hookResult.canInteract).toBe(true);
    expect(hookResult.userRole).toBe(ROLES.ORG_ADMIN);
  });

  it('should return correct permissions for staff', () => {
    setMockUser(ROLES.ORG_STAFF);

    let hookResult;
    function TestComponent() {
      hookResult = useWidgetPermissions('decision-queue');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.canView).toBe(true);
    expect(hookResult.canInteract).toBe(false); // Staff can't interact with decision-queue
    expect(hookResult.userRole).toBe(ROLES.ORG_STAFF);
  });

  it('should return correct permissions for viewer', () => {
    setMockUser(ROLES.ORG_VIEWER);

    let hookResult;
    function TestComponent() {
      hookResult = useWidgetPermissions('patient-dashboard');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.canView).toBe(true);
    expect(hookResult.canInteract).toBe(true);
    expect(hookResult.userRole).toBe(ROLES.ORG_VIEWER);
  });

  it('should return false for non-existent widget', () => {
    setMockUser(ROLES.ORG_ADMIN);

    let hookResult;
    function TestComponent() {
      hookResult = useWidgetPermissions('non-existent');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.canView).toBe(false);
    expect(hookResult.canInteract).toBe(false);
  });
});

describe('useFeaturePermission hook', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should return correct permission for admin', () => {
    setMockUser(ROLES.ORG_ADMIN);

    let hookResult;
    function TestComponent() {
      hookResult = useFeaturePermission('approve-suggestions');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.hasPermission).toBe(true);
    expect(hookResult.userRole).toBe(ROLES.ORG_ADMIN);
  });

  it('should return correct permission for staff', () => {
    setMockUser(ROLES.ORG_STAFF);

    let hookResult;
    function TestComponent() {
      hookResult = useFeaturePermission('approve-suggestions');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.hasPermission).toBe(false);
    expect(hookResult.userRole).toBe(ROLES.ORG_STAFF);
  });

  it('should return correct permission for viewer', () => {
    setMockUser(ROLES.ORG_VIEWER);

    let hookResult;
    function TestComponent() {
      hookResult = useFeaturePermission('create-appointment');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.hasPermission).toBe(true);
    expect(hookResult.userRole).toBe(ROLES.ORG_VIEWER);
  });

  it('should return false for non-existent feature', () => {
    setMockUser(ROLES.ORG_ADMIN);

    let hookResult;
    function TestComponent() {
      hookResult = useFeaturePermission('non-existent-feature');
      return null;
    }

    render(<TestComponent />);

    expect(hookResult.hasPermission).toBe(false);
  });
});

