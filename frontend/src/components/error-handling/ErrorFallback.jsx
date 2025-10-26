/**
 * ErrorFallback Component
 * 
 * Displays a user-friendly error message when an error boundary catches an error.
 * Provides options to retry or report the error.
 * 
 * @component
 */

import React from 'react';
import PropTypes from 'prop-types';
import './ErrorFallback.css';
import { AlertTriangle, RefreshCw, Home, Mail } from 'lucide-react';
import { Button } from '@/components/ui/button';

/**
 * ErrorFallback Component
 * 
 * @param {Object} props
 * @param {Error} props.error - The error that was caught
 * @param {Object} props.errorInfo - React error info with component stack
 * @param {Function} props.onReset - Callback to reset the error boundary
 */
export default function ErrorFallback({ error, errorInfo, onReset }) {
  const isDevelopment = process.env.NODE_ENV === 'development';

  const handleReload = () => {
    window.location.reload();
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReportError = () => {
    const subject = encodeURIComponent('DentaFlow Error Report');
    const body = encodeURIComponent(
      `Error: ${error?.message || 'Unknown error'}\n\n` +
      `Stack: ${error?.stack || 'No stack trace'}\n\n` +
      `Component Stack: ${errorInfo?.componentStack || 'No component stack'}\n\n` +
      `Timestamp: ${new Date().toISOString()}\n\n` +
      `User Agent: ${navigator.userAgent}`
    );
    window.location.href = `mailto:support@dentaflow.ai?subject=${subject}&body=${body}`;
  };

  return (
    <div className="error-fallback-container">
      <div className="error-fallback-content">
        {/* Error Icon */}
        <div className="error-fallback-icon">
          <AlertTriangle className="w-16 h-16 text-red-500" />
        </div>

        {/* Error Title */}
        <h1 className="error-fallback-title">
          Oops! Something went wrong
        </h1>

        {/* Error Description */}
        <p className="error-fallback-description">
          We're sorry, but something unexpected happened. 
          Please try refreshing the page or contact support if the problem persists.
        </p>

        {/* Development Error Details */}
        {isDevelopment && error && (
          <div className="error-fallback-details">
            <h2 className="error-fallback-details-title">Error Details (Development Only)</h2>
            <div className="error-fallback-error-message">
              <strong>Error:</strong> {error.message}
            </div>
            {error.stack && (
              <pre className="error-fallback-stack">
                {error.stack}
              </pre>
            )}
            {errorInfo?.componentStack && (
              <details className="error-fallback-component-stack">
                <summary>Component Stack</summary>
                <pre>{errorInfo.componentStack}</pre>
              </details>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="error-fallback-actions">
          <Button
            onClick={onReset || handleReload}
            className="error-fallback-btn error-fallback-btn-primary"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>

          <Button
            onClick={handleGoHome}
            variant="outline"
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            <Home className="w-4 h-4 mr-2" />
            Go Home
          </Button>

          <Button
            onClick={handleReportError}
            variant="outline"
            className="error-fallback-btn error-fallback-btn-secondary"
          >
            <Mail className="w-4 h-4 mr-2" />
            Report Error
          </Button>
        </div>

        {/* Support Info */}
        <div className="error-fallback-support">
          <p>
            Need help? Contact us at{' '}
            <a href="mailto:support@dentaflow.ai" className="error-fallback-link">
              support@dentaflow.ai
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

ErrorFallback.propTypes = {
  error: PropTypes.instanceOf(Error),
  errorInfo: PropTypes.shape({
    componentStack: PropTypes.string
  }),
  onReset: PropTypes.func
};

