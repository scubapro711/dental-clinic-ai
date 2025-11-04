/**
 * Organization Service
 * 
 * Handles multi-tenancy operations:
 * - Get/set current organization context
 * - Fetch user's organizations
 * - Switch between organizations
 * - Register new organizations
 * 
 * Organization context is stored in localStorage:
 * - current_organization_id: UUID of current organization
 * 
 * All API calls automatically include X-Organization-ID header
 * via api client interceptor (src/api/client.ts).
 * 
 * @example
 * ```typescript
 * import { organizationService } from '@/services/organizationService';
 * 
 * // Get current organization ID
 * const orgId = organizationService.getCurrentOrganizationId();
 * 
 * // Get user's organizations
 * const orgs = await organizationService.getUserOrganizations();
 * 
 * // Switch organization
 * organizationService.switchOrganization('new-org-id');
 * ```
 */

import { api } from '../api/client';
import type {
  Organization,
  OrganizationMembership,
  OrganizationContext,
  OrganizationRegisterRequest,
  OrganizationRegisterResponse,
} from '../types/organization';

export const organizationService = {
  /**
   * Get current organization ID from localStorage
   * 
   * @returns Organization ID or null if not set
   * 
   * @example
   * ```typescript
   * const orgId = organizationService.getCurrentOrganizationId();
   * if (!orgId) {
   *   console.error('No organization selected');
   * }
   * ```
   */
  getCurrentOrganizationId: (): string | null => {
    return localStorage.getItem('current_organization_id');
  },

  /**
   * Set current organization ID in localStorage
   * 
   * @param organizationId - Organization ID to set
   * 
   * @example
   * ```typescript
   * organizationService.setCurrentOrganizationId('org-uuid');
   * ```
   */
  setCurrentOrganizationId: (organizationId: string): void => {
    localStorage.setItem('current_organization_id', organizationId);
  },

  /**
   * Clear current organization ID from localStorage
   * 
   * @example
   * ```typescript
   * organizationService.clearCurrentOrganizationId();
   * ```
   */
  clearCurrentOrganizationId: (): void => {
    localStorage.removeItem('current_organization_id');
  },

  /**
   * Get user's organization memberships
   * 
   * Returns all organizations the current user belongs to.
   * 
   * @returns Promise with array of memberships
   * @throws {AxiosError} If API call fails
   * 
   * @example
   * ```typescript
   * const memberships = await organizationService.getUserOrganizations();
   * console.log(`User belongs to ${memberships.length} organizations`);
   * ```
   */
  getUserOrganizations: async (): Promise<OrganizationMembership[]> => {
    const response = await api.get<OrganizationMembership[]>(
      '/users/me/organizations'
    );
    return response.data;
  },

  /**
   * Get organization details by ID
   * 
   * @param organizationId - Organization ID
   * @returns Promise with organization details
   * @throws {AxiosError} If API call fails or not found
   * 
   * @example
   * ```typescript
   * const org = await organizationService.getOrganization('org-uuid');
   * console.log(`Organization: ${org.name}`);
   * ```
   */
  getOrganization: async (organizationId: string): Promise<Organization> => {
    const response = await api.get<Organization>(
      `/organizations/${organizationId}`
    );
    return response.data;
  },

  /**
   * Get current organization context
   * 
   * Fetches full details of current organization.
   * 
   * @returns Promise with organization context or null
   * @throws {AxiosError} If API call fails
   * 
   * @example
   * ```typescript
   * const context = await organizationService.getCurrentOrganizationContext();
   * if (context) {
   *   console.log(`Current org: ${context.organization.name}`);
   *   console.log(`Your role: ${context.membership.organization_role}`);
   * }
   * ```
   */
  getCurrentOrganizationContext: async (): Promise<OrganizationContext | null> => {
    const organizationId = organizationService.getCurrentOrganizationId();
    if (!organizationId) {
      return null;
    }

    try {
      const [organization, memberships] = await Promise.all([
        organizationService.getOrganization(organizationId),
        organizationService.getUserOrganizations(),
      ]);

      const membership = memberships.find(
        (m) => m.organization_id === organizationId
      );

      if (!membership) {
        console.warn('User is not a member of current organization');
        return null;
      }

      return {
        organization,
        membership,
      };
    } catch (error) {
      console.error('Failed to get organization context:', error);
      return null;
    }
  },

  /**
   * Switch to a different organization
   * 
   * Updates localStorage and dispatches 'organizationChanged' event.
   * Components listening to this event will reload their data.
   * 
   * @param organizationId - Organization ID to switch to
   * 
   * @example
   * ```typescript
   * organizationService.switchOrganization('new-org-id');
   * // All widgets will reload with new organization context
   * ```
   */
  switchOrganization: (organizationId: string): void => {
    organizationService.setCurrentOrganizationId(organizationId);
    
    // Dispatch event for components to react
    window.dispatchEvent(
      new CustomEvent('organizationChanged', {
        detail: { organizationId },
      })
    );
  },

  /**
   * Register a new organization (clinic onboarding)
   * 
   * Creates new organization, owner user, and default settings.
   * Returns access token for immediate login.
   * 
   * @param data - Registration request data
   * @returns Promise with registration response
   * @throws {AxiosError} If registration fails
   * 
   * @example
   * ```typescript
   * const response = await organizationService.registerOrganization({
   *   clinic_name: 'Dr. Cohen Dental',
   *   clinic_email: 'info@cohen-dental.com',
   *   owner_full_name: 'Dr. Rachel Cohen',
   *   owner_email: 'rachel@cohen-dental.com',
   *   owner_password: 'SecurePass123!',
   * });
   * 
   * // Save token and organization ID
   * localStorage.setItem('access_token', response.access_token);
   * organizationService.setCurrentOrganizationId(response.organization_id);
   * ```
   */
  registerOrganization: async (
    data: OrganizationRegisterRequest
  ): Promise<OrganizationRegisterResponse> => {
    const response = await api.post<OrganizationRegisterResponse>(
      '/organizations/register',
      data
    );
    return response.data;
  },
};

export default organizationService;
