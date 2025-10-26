import React from 'react';
import * as Sentry from '@sentry/react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Error Boundary Component
 * 
 * Catches React errors and displays a fallback UI instead of crashing.
 * Critical for production stability.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('Error Boundary caught an error:', error, errorInfo);
    
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // Send error to Sentry in production
    if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
      Sentry.withScope((scope) => {
        scope.setExtras(errorInfo);
        scope.setTag('error_boundary', 'true');
        Sentry.captureException(error);
      });
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    
    // Optionally reload the page if errors persist
    if (this.state.errorCount > 3) {
      window.location.reload();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
          <Card className="max-w-2xl w-full shadow-lg">
            <CardHeader className="bg-red-50 border-b border-red-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                  <AlertCircle className="w-6 h-6 text-red-600" />
                </div>
                <div>
                  <CardTitle className="text-red-900">Something went wrong</CardTitle>
                  <p className="text-sm text-red-700 mt-1">
                    The application encountered an unexpected error
                  </p>
                </div>
              </div>
            </CardHeader>
            
            <CardContent className="p-6">
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Error Details:</h3>
                  <div className="bg-gray-100 rounded-lg p-4 font-mono text-sm text-gray-800 overflow-auto max-h-40">
                    {this.state.error?.toString()}
                  </div>
                </div>

                {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Component Stack:</h3>
                    <div className="bg-gray-100 rounded-lg p-4 font-mono text-xs text-gray-700 overflow-auto max-h-60">
                      {this.state.errorInfo.componentStack}
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <Button
                    onClick={this.handleReset}
                    className="flex items-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Try Again
                  </Button>
                  
                  <Button
                    variant="outline"
                    onClick={() => window.location.reload()}
                  >
                    Reload Page
                  </Button>
                </div>

                {this.state.errorCount > 2 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
                    <p className="font-semibold mb-1">Persistent Error Detected</p>
                    <p>
                      This error has occurred {this.state.errorCount} times. 
                      If the problem persists, please contact support or try clearing your browser cache.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
