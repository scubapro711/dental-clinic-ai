import React, { useState, useEffect } from 'react';
import { CreditCard, Lock, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { API_BASE_URL } from '@/config';

/**
 * Payment Method Form Component
 * 
 * Form for adding or updating payment methods using Stripe.
 * Features:
 * - Stripe Elements integration
 * - Card validation
 * - Secure payment processing
 * - Error handling
 */
export default function PaymentMethodForm({ onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stripeLoaded, setStripeLoaded] = useState(false);
  const [cardElement, setCardElement] = useState(null);

  useEffect(() => {
    // Load Stripe.js
    const script = document.createElement('script');
    script.src = 'https://js.stripe.com/v3/';
    script.async = true;
    script.onload = () => {
      setStripeLoaded(true);
      initializeStripe();
    };
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const initializeStripe = async () => {
    try {
      // Get publishable key from backend
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/stripe-key`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to get Stripe key');
      }

      const data = await response.json();
      const stripe = window.Stripe(data.publishable_key);
      const elements = stripe.elements();
      
      const card = elements.create('card', {
        style: {
          base: {
            fontSize: '16px',
            color: '#424770',
            '::placeholder': {
              color: '#aab7c4',
            },
          },
          invalid: {
            color: '#9e2146',
          },
        },
      });

      card.mount('#card-element');
      setCardElement({ stripe, card });

    } catch (err) {
      console.error('Error initializing Stripe:', err);
      setError('Failed to load payment form. Please refresh the page.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!cardElement) {
      setError('Payment form not loaded. Please refresh the page.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const { stripe, card } = cardElement;

      // Create payment method
      const { error: stripeError, paymentMethod } = await stripe.createPaymentMethod({
        type: 'card',
        card: card,
      });

      if (stripeError) {
        setError(stripeError.message);
        setLoading(false);
        return;
      }

      // Send payment method to backend
      const response = await fetch(`${API_BASE_URL}/api/v1/subscriptions/payment-method`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          payment_method_id: paymentMethod.id
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update payment method');
      }

      // Success
      if (onSuccess) {
        onSuccess();
      }

    } catch (err) {
      console.error('Error updating payment method:', err);
      setError(err.message || 'Failed to update payment method. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" dir="rtl">
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-900">{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        <div>
          <Label htmlFor="card-element">פרטי כרטיס אשראי</Label>
          <div 
            id="card-element" 
            className="mt-2 p-3 border border-gray-300 rounded-md bg-white"
            style={{ minHeight: '40px' }}
          />
          {!stripeLoaded && (
            <div className="mt-2 text-sm text-gray-500">טוען טופס תשלום...</div>
          )}
        </div>

        <Alert className="border-blue-200 bg-blue-50">
          <Lock className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-900 text-sm">
            התשלום שלך מאובטח באמצעות Stripe. אנחנו לא שומרים את פרטי כרטיס האשראי שלך.
          </AlertDescription>
        </Alert>
      </div>

      <div className="flex gap-3">
        <Button
          type="submit"
          disabled={loading || !stripeLoaded}
          className="flex-1"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white ml-2"></div>
              שומר...
            </>
          ) : (
            <>
              <CreditCard className="h-4 w-4 ml-2" />
              שמור אמצעי תשלום
            </>
          )}
        </Button>
      </div>
    </form>
  );
}

