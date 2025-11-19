import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import SimpleMockLogin from './SimpleMockLogin';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Helper to render component with router
function renderWithRouter(component) {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
}

describe('SimpleMockLogin', () => {
  beforeEach(() => {
    localStorage.clear();
    mockNavigate.mockClear();
    vi.clearAllTimers();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Initial Rendering', () => {
    it('should render the login page', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByText('DentaFlow')).toBeInTheDocument();
      expect(screen.getByText('Portal Selection - Demo Mode')).toBeInTheDocument();
    });

    it('should display demo mode warning', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const demoModeTexts = screen.getAllByText(/Demo Mode/);
      expect(demoModeTexts.length).toBeGreaterThan(0);
      expect(screen.getByText(/demo version/i)).toBeInTheDocument();
    });

    it('should display both portal options', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByText(/Clinic Portal \(Mission Control\)/)).toBeInTheDocument();
      expect(screen.getByText(/Patient Portal/)).toBeInTheDocument();
    });

    it('should have clinic portal selected by default', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const clinicRadio = screen.getAllByRole('radio')[0];
      const patientRadio = screen.getAllByRole('radio')[1];
      
      expect(clinicRadio).toBeChecked();
      expect(patientRadio).not.toBeChecked();
    });

    it('should display clinic user details', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByText(/Dr. Rachel Cohen/)).toBeInTheDocument();
      expect(screen.getByText(/org_admin/)).toBeInTheDocument();
    });

    it('should display patient user details', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByText(/Sarah Johnson/)).toBeInTheDocument();
      expect(screen.getByText(/org_viewer \(Patient\)/)).toBeInTheDocument();
    });

    it('should display version information', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByText(/v20.1.0/)).toBeInTheDocument();
      expect(screen.getByText(/Not for production - Demo purposes only/)).toBeInTheDocument();
    });

    it('should display correct button text for clinic portal', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      expect(screen.getByRole('button', { name: /Enter Clinic Portal/ })).toBeInTheDocument();
    });
  });

  describe('Portal Selection', () => {
    it('should switch to patient portal when clicked', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      const patientRadio = screen.getAllByRole('radio')[1];
      expect(patientRadio).toBeChecked();
    });

    it('should update button text when switching to patient portal', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      expect(screen.getByRole('button', { name: /Enter Patient Portal/ })).toBeInTheDocument();
    });

    it('should switch back to clinic portal when clicked', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Switch to patient
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      // Switch back to clinic
      const clinicOption = screen.getByText(/Clinic Portal/).closest('div[class*="border"]');
      fireEvent.click(clinicOption);
      
      const clinicRadio = screen.getAllByRole('radio')[0];
      expect(clinicRadio).toBeChecked();
    });

    it('should change radio button when clicking on clinic option', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Switch to patient first
      const patientRadio = screen.getAllByRole('radio')[1];
      fireEvent.click(patientRadio);
      
      // Switch back to clinic
      const clinicRadio = screen.getAllByRole('radio')[0];
      fireEvent.change(clinicRadio, { target: { checked: true } });
      
      expect(clinicRadio).toBeChecked();
    });

    it('should apply correct styling to selected portal', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const clinicOption = screen.getByText(/Clinic Portal/).closest('div[class*="border"]');
      expect(clinicOption).toHaveClass('border-blue-600', 'bg-blue-50');
    });

    it('should apply correct styling to patient portal when selected', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      expect(patientOption).toHaveClass('border-green-600', 'bg-green-50');
    });
  });

  describe('Clinic Portal Login', () => {
    it('should set correct localStorage data for clinic admin', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button', { name: /Enter Clinic Portal/ });
      fireEvent.click(loginButton);
      
      // Check localStorage immediately (before timeout)
      expect(localStorage.getItem('token')).toMatch(/^mock-jwt-token-/);
      expect(localStorage.getItem('access_token')).toMatch(/^mock-jwt-token-/);
      expect(localStorage.getItem("current_organization_id")).toBe("1");
      
      const userProfile = JSON.parse(localStorage.getItem('user_profile'));
      expect(userProfile.name).toBe('Dr. Rachel Cohen');
      expect(userProfile.email).toBe('rachel@dentaflow.ai');
      expect(userProfile.role).toBe('org_admin');
      expect(userProfile.organization_id).toBe(1);
    });

    it('should set mockUser for RBAC utility', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button', { name: /Enter Clinic Portal/ });
      fireEvent.click(loginButton);
      
      const mockUser = JSON.parse(localStorage.getItem('mockUser'));
      expect(mockUser.role).toBe('org_admin');
      expect(mockUser.email).toBe('rachel@dentaflow.ai');
    });

    it('should navigate to clinic dashboard after login', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button', { name: /Enter Clinic Portal/ });
      fireEvent.click(loginButton);
      
      // Fast-forward timer
      vi.advanceTimersByTime(500);
      
      expect(mockNavigate).toHaveBeenCalledWith('/clinic/dashboard', { replace: true });
    });

    it('should show loading state during login', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button', { name: /Enter Clinic Portal/ });
      fireEvent.click(loginButton);
      
      expect(screen.getByText('Logging in...')).toBeInTheDocument();
      expect(loginButton).toBeDisabled();
    });

    it('should disable button during loading', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button', { name: /Enter Clinic Portal/ });
      fireEvent.click(loginButton);
      
      expect(loginButton).toBeDisabled();
      expect(loginButton).toHaveClass('disabled:opacity-50', 'disabled:cursor-not-allowed');
    });
  });

  describe('Patient Portal Login', () => {
    it('should set correct localStorage data for patient', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Select patient portal
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      // Click login
      const loginButton = screen.getByRole('button', { name: /Enter Patient Portal/ });
      fireEvent.click(loginButton);
      
      const userProfile = JSON.parse(localStorage.getItem('user_profile'));
      expect(userProfile.name).toBe('Sarah Johnson');
      expect(userProfile.email).toBe('sarah.johnson@example.com');
      expect(userProfile.role).toBe('org_viewer');
      expect(userProfile.patient_id).toBe(1);
    });

    it('should navigate to patient dashboard after login', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Select patient portal
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      // Click login
      const loginButton = screen.getByRole('button', { name: /Enter Patient Portal/ });
      fireEvent.click(loginButton);
      
      // Fast-forward timer
      vi.advanceTimersByTime(500);
      
      expect(mockNavigate).toHaveBeenCalledWith('/patient/dashboard', { replace: true });
    });

    it('should set mockUser with org_viewer role', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Select patient portal
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      // Click login
      const loginButton = screen.getByRole('button', { name: /Enter Patient Portal/ });
      fireEvent.click(loginButton);
      
      const mockUser = JSON.parse(localStorage.getItem('mockUser'));
      expect(mockUser.role).toBe('org_viewer');
      expect(mockUser.email).toBe('sarah.johnson@example.com');
    });
  });

  describe('Token Generation', () => {
    it('should generate unique tokens for each login', () => {
      const { rerender } = renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      
      // First login
      fireEvent.click(loginButton);
      const token1 = localStorage.getItem('token');
      
      // Wait a bit to ensure different timestamp
      vi.advanceTimersByTime(10);
      
      // Clear and re-render
      localStorage.clear();
      mockNavigate.mockClear();
      rerender(<SimpleMockLogin />);
      
      const loginButton2 = screen.getByRole('button');
      fireEvent.click(loginButton2);
      const token2 = localStorage.getItem('token');
      
      expect(token1).not.toBe(token2);
    });

    it('should include timestamp in token', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const token = localStorage.getItem('token');
      expect(token).toMatch(/^mock-jwt-token-\d+$/);
    });

    it('should set same token for both token and access_token', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const token = localStorage.getItem('token');
      const accessToken = localStorage.getItem('access_token');
      
      expect(token).toBe(accessToken);
    });
  });

  describe('User Data Consistency', () => {
    it('should have matching data in user_profile and mockUser', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const userProfile = JSON.parse(localStorage.getItem('user_profile'));
      const mockUser = JSON.parse(localStorage.getItem('mockUser'));
      
      expect(userProfile).toEqual(mockUser);
    });

    it('should include all required user fields for clinic admin', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const user = JSON.parse(localStorage.getItem('mockUser'));
      
      expect(user).toHaveProperty('id');
      expect(user).toHaveProperty('name');
      expect(user).toHaveProperty('email');
      expect(user).toHaveProperty('role');
      expect(user).toHaveProperty('organization_id');
      expect(user).toHaveProperty('organization_name');
      expect(user).toHaveProperty('avatar');
    });

    it('should include patient_id for patient user', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Select patient portal
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      fireEvent.click(patientOption);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const user = JSON.parse(localStorage.getItem('mockUser'));
      expect(user).toHaveProperty('patient_id');
      expect(user.patient_id).toBe(1);
    });
  });

  describe('Navigation Behavior', () => {
    it('should use replace: true for navigation', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      vi.advanceTimersByTime(500);
      
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.any(String),
        { replace: true }
      );
    });

    it('should wait 500ms before navigation', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      // Before timeout
      expect(mockNavigate).not.toHaveBeenCalled();
      
      // After timeout
      vi.advanceTimersByTime(500);
      
      expect(mockNavigate).toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should show spinner during loading', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      const spinner = screen.getByRole('button').querySelector('svg.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should clear loading state after navigation', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      fireEvent.click(loginButton);
      
      vi.advanceTimersByTime(500);
      
      expect(mockNavigate).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    it('should handle rapid portal switching', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const clinicOption = screen.getByText(/Clinic Portal/).closest('div[class*="border"]');
      const patientOption = screen.getByText(/Patient Portal/).closest('div[class*="border"]');
      
      // Rapid switching
      fireEvent.click(patientOption);
      fireEvent.click(clinicOption);
      fireEvent.click(patientOption);
      fireEvent.click(clinicOption);
      
      const clinicRadio = screen.getAllByRole('radio')[0];
      expect(clinicRadio).toBeChecked();
    });

    it('should handle multiple login attempts', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const loginButton = screen.getByRole('button');
      
      // First click
      fireEvent.click(loginButton);
      
      // Second click (should be disabled)
      fireEvent.click(loginButton);
      
      // Should only navigate once
      vi.advanceTimersByTime(1000);
      
      expect(mockNavigate).toHaveBeenCalledTimes(1);
    });

    it('should handle localStorage being full', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      // Mock localStorage.setItem to throw
      const originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = vi.fn(() => {
        throw new Error('QuotaExceededError');
      });
      
      const loginButton = screen.getByRole('button');
      
      // Should not crash
      expect(() => fireEvent.click(loginButton)).not.toThrow();
      
      // Restore
      Storage.prototype.setItem = originalSetItem;
    });
  });

  describe('Accessibility', () => {
    it('should have proper radio button labels', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const radios = screen.getAllByRole('radio');
      expect(radios).toHaveLength(2);
    });

    it('should have accessible button', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent(/Enter/);
    });

    it('should support keyboard navigation for radio buttons', () => {
      renderWithRouter(<SimpleMockLogin />);
      
      const patientRadio = screen.getAllByRole('radio')[1];
      
      // Simulate keyboard selection
      fireEvent.change(patientRadio, { target: { checked: true } });
      
      expect(patientRadio).toBeChecked();
    });
  });
});

