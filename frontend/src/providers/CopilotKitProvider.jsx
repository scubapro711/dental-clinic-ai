import React from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';

export const CopilotKitProvider = ({ children }) => {
  // Use base URL without /api/v1 to avoid duplication
  const BASE_URL = 'http://localhost:8000';
  
  return (
    <CopilotKit
      runtimeUrl={`${BASE_URL}/api/v1/copilotkit`}
      agent="dental_assistant"
    >
      {children}
    </CopilotKit>
  );
};

export default CopilotKitProvider;
