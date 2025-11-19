import React, { createContext, useContext } from 'react';
import { SUBSCRIPTION_PLANS } from '../constants/agenticDashboard';

const SubscriptionContext = createContext(null);

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    return { 
      plan: SUBSCRIPTION_PLANS['starter'], 
      hasFeature: () => false 
    };
  }
  return context;
};

export const SubscriptionProvider = ({ children, organization }) => {
  const planKey = organization?.plan || 'starter';
  const plan = SUBSCRIPTION_PLANS[planKey];

  const hasFeature = (featureKey) => {
    if (planKey === 'enterprise') return true;
    return plan.features.includes(featureKey);
  };

  return (
    <SubscriptionContext.Provider value={{ plan, hasFeature }}>
      {children}
    </SubscriptionContext.Provider>
  );
};
