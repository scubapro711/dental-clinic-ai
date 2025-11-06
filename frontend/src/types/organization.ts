/**
 * Organization Types
 * 
 * Multi-tenancy support for DentaFlow.
 * Each dental clinic is an organization.
 * 
 * Backend: app/models/organization.py
 */

/**
 * Subscription tier for pricing
 */
export enum SubscriptionTier {
  Basic = 'basic',
  Professional = 'professional',
  Enterprise = 'enterprise',
}

/**
 * Subscription status
 */
export enum SubscriptionStatus {
  Active = 'active',
  Trial = 'trial',
  Suspended = 'suspended',
  Cancelled = 'cancelled',
}

/**
 * Organization role in membership
 */
export enum OrganizationRole {
  Owner = 'owner',
  Manager = 'manager',
  Staff = 'staff',
  Patient = 'patient',
}

/**
 * Organization entity (dental clinic)
 */
export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  
  // Contact
  email: string;
  phone?: string;
  address?: string;
  
  // Subscription
  subscription_tier: SubscriptionTier;
  subscription_status: SubscriptionStatus;
  subscription_start_date?: string;
  subscription_end_date?: string;
  
  // Billing
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  
  // Odoo Integration
  odoo_db_name?: string;
  
  // Status
  is_active: boolean;
  
  // Timestamps
  created_at: string;
  updated_at: string;
}

/**
 * User's membership in an organization
 */
export interface OrganizationMembership {
  id: string;
  user_id: string;
  organization_id: string;
  
  // Organization details (denormalized for convenience)
  organization_name: string;
  organization_slug: string;
  
  // Roles
  organization_role: OrganizationRole;
  functional_role?: string;  // dentist, hygienist, receptionist, etc.
  
  // Odoo link
  odoo_partner_id?: number;
  
  // Status
  is_active: boolean;
  joined_at: string;
}

/**
 * Current organization context
 */
export interface OrganizationContext {
  organization: Organization;
  membership: OrganizationMembership;
}

/**
 * Organization registration request
 */
export interface OrganizationRegisterRequest {
  // Clinic info
  clinic_name: string;
  clinic_email: string;
  clinic_phone?: string;
  clinic_address?: string;
  
  // Owner info
  owner_full_name: string;
  owner_email: string;
  owner_password: string;
  owner_phone?: string;
}

/**
 * Organization registration response
 */
export interface OrganizationRegisterResponse {
  organization_id: string;
  organization_name: string;
  organization_slug: string;
  owner_id: string;
  owner_email: string;
  access_token: string;
  token_type: string;
  message: string;
}

/**
 * Agent availability by subscription tier
 */
export const AGENTS_BY_TIER: Record<SubscriptionTier, string[]> = {
  [SubscriptionTier.Basic]: ['alex', 'sarah', 'harper', 'sophia'],
  [SubscriptionTier.Professional]: ['alex', 'sarah', 'harper', 'sophia', 'marcus'],
  [SubscriptionTier.Enterprise]: ['alex', 'sarah', 'harper', 'sophia', 'marcus', 'cfo', 'cto'],
};

/**
 * Check if agent is available in subscription tier
 * 
 * @param agentName - Name of the agent
 * @param tier - Subscription tier
 * @returns true if agent is available in tier
 * 
 * @example
 * ```typescript
 * const canUseAgent = isAgentAvailable('marcus', SubscriptionTier.Professional);
 * // true
 * ```
 */
export function isAgentAvailable(agentName: string, tier: SubscriptionTier): boolean {
  return AGENTS_BY_TIER[tier].includes(agentName.toLowerCase());
}

/**
 * Get subscription tier display name
 * 
 * @param tier - Subscription tier
 * @returns Display name with pricing
 * 
 * @example
 * ```typescript
 * const displayName = getSubscriptionTierName(SubscriptionTier.Professional);
 * // "Professional ($1,500/month)"
 * ```
 */
export function getSubscriptionTierName(tier: SubscriptionTier): string {
  switch (tier) {
    case SubscriptionTier.Basic:
      return 'Basic (Free)';
    case SubscriptionTier.Professional:
      return 'Professional ($1,500/month)';
    case SubscriptionTier.Enterprise:
      return 'Enterprise ($4,500/month)';
  }
}

/**
 * Get subscription status display name
 * 
 * @param status - Subscription status
 * @returns Display name
 * 
 * @example
 * ```typescript
 * const displayName = getSubscriptionStatusName(SubscriptionStatus.Trial);
 * // "Trial"
 * ```
 */
export function getSubscriptionStatusName(status: SubscriptionStatus): string {
  switch (status) {
    case SubscriptionStatus.Active:
      return 'Active';
    case SubscriptionStatus.Trial:
      return 'Trial';
    case SubscriptionStatus.Suspended:
      return 'Suspended';
    case SubscriptionStatus.Cancelled:
      return 'Cancelled';
  }
}
