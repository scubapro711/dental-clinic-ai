// Mock API Client for development

import { AGENTS_ROSTER, MOCK_USERS, MOCK_ORG } from '../utils/agentic_dashboard/constants';

// FILE 2: API CLIENT (src/api/client.js)
// ==========================================

const mockApiClient = {
  // Flow 1 & 2: Login Logic
  login: async (email, password) => {
      await new Promise(r => setTimeout(r, 800)); // Simulate network delay
      
      const user = MOCK_USERS[email];
      // Check demo credentials (demo123)
      if (user && password === 'demo123') {
          return {
              access_token: 'mock_access_token_' + Date.now(),
              refresh_token: 'mock_refresh_token_' + Date.now(),
              user: user,
              organization: MOCK_ORG
          };
      }
      throw new Error('AUTHENTICATION_FAILED');
  },

  get: async (endpoint, orgId) => {
    // Flow 3: Security Check
    if (!orgId && !endpoint.includes('/auth')) {
      console.error(`[CRITICAL] 🛑 API Call Blocked! Missing X-Organization-ID header.`);
      throw new Error("Security Violation: Missing Organization Context");
    }
    console.log(`[API] ✅ GET ${endpoint}`);
    
    await new Promise(r => setTimeout(r, 300));

    if (endpoint === '/decisions/pending') {
      return {
        decisions: [
          { 
            id: 'dec-001', 
            agent_id: AGENTS_ROSTER.MARCUS.id,
            agent_name: `${AGENTS_ROSTER.MARCUS.name} (${AGENTS_ROSTER.MARCUS.role})`,
            category: 'billing_approval',
            title: 'אישור הנחה חריגה (15%)', 
            description: 'מטופל וותיק, ביקש הנחה עקב המצב הכלכלי.',
            priority: 'high', 
            confidence: 88 
          },
          { 
            id: 'dec-002', 
            agent_id: AGENTS_ROSTER.SARAH.id,
            agent_name: `${AGENTS_ROSTER.SARAH.name} (${AGENTS_ROSTER.SARAH.role})`,
            category: 'treatment_plan',
            title: 'שינוי תוכנית טיפול', 
            description: 'זוהתה עששת עמוקה יותר מהצפוי בשן 36 בצילום החדש.',
            priority: 'medium', 
            confidence: 92 
          }
        ]
      };
    }
    
    if (endpoint === '/auth/me') {
       // Simulate fetching user from token
       // In real app, decoding JWT happens here or on server
       return { ...MOCK_USERS['rachel@dentaflow.ai'], permissions: ['view_dashboard', 'view_patients', 'view_financials', 'edit_clinical_records'] };
    }

    return { success: true };
  }
};


export default mockApiClient;
