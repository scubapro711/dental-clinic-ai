/**
 * Organization Selector Component
 * 
 * Dropdown to switch between organizations.
 * Only visible if user belongs to multiple organizations.
 * 
 * Features:
 * - Fetches user's organizations on mount
 * - Shows current organization
 * - Allows switching between organizations
 * - Dispatches 'organizationChanged' event on switch
 * - Hides if user has only one organization
 * 
 * @example
 * ```jsx
 * import { OrganizationSelector } from '@/components/OrganizationSelector';
 * 
 * <DashboardHeader>
 *   <OrganizationSelector />
 *   <AgentCards />
 * </DashboardHeader>
 * ```
 */

import React, { useState, useEffect } from 'react';
import { organizationService } from '../services/organizationService';
import './OrganizationSelector.css';

export const OrganizationSelector = () => {
  const [organizations, setOrganizations] = useState([]);
  const [currentOrgId, setCurrentOrgId] = useState(
    organizationService.getCurrentOrganizationId()
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch user's organizations on mount
  useEffect(() => {
    const fetchOrganizations = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const orgs = await organizationService.getUserOrganizations();
        setOrganizations(orgs);
        
        // If no current organization set, set to first one
        if (!currentOrgId && orgs.length > 0) {
          const firstOrgId = orgs[0].organization_id;
          organizationService.setCurrentOrganizationId(firstOrgId);
          setCurrentOrgId(firstOrgId);
        }
      } catch (err) {
        console.error('Failed to fetch organizations:', err);
        setError('Failed to load organizations');
      } finally {
        setLoading(false);
      }
    };

    fetchOrganizations();
  }, [currentOrgId]);

  // Handle organization switch
  const handleSwitch = (orgId) => {
    organizationService.switchOrganization(orgId);
    setCurrentOrgId(orgId);
  };

  // Don't show if loading
  if (loading) {
    return (
      <div className="organization-selector loading">
        <span>Loading organizations...</span>
      </div>
    );
  }

  // Don't show if error
  if (error) {
    return (
      <div className="organization-selector error">
        <span>{error}</span>
      </div>
    );
  }

  // Don't show if user has only one organization
  if (organizations.length <= 1) {
    return null;
  }

  // Find current organization
  const currentOrg = organizations.find(
    (org) => org.organization_id === currentOrgId
  );

  return (
    <div className="organization-selector">
      <label htmlFor="org-select" className="sr-only">
        Select Organization
      </label>
      <select
        id="org-select"
        className="organization-select"
        value={currentOrgId || ''}
        onChange={(e) => handleSwitch(e.target.value)}
        aria-label="Select organization"
      >
        {organizations.map((org) => (
          <option key={org.id} value={org.organization_id}>
            {org.organization_name} ({org.organization_role})
          </option>
        ))}
      </select>
      
      {currentOrg && (
        <div className="current-org-info">
          <span className="org-name">{currentOrg.organization_name}</span>
          <span className="org-role">{currentOrg.organization_role}</span>
        </div>
      )}
    </div>
  );
};

export default OrganizationSelector;
