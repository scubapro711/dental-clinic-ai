import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Revenue Widget - Marcus CFO Agent
 * 
 * Shows revenue overview with trends and insights
 * Connected to real OdooClient API
 */
export default function RevenueWidget({ onChatWithAgent }) {
  const [revenue, setRevenue] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRevenue();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchRevenue, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchRevenue = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch('http://localhost:8000/api/v1/dashboard/widgets/revenue/summary', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || 'demo_token'}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setRevenue(data);
    } catch (error) {
      console.error('Error fetching revenue:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const handleViewDetails = () => {
    if (onChatWithAgent) {
      onChatWithAgent('מרקוס, תן לי פירוט מלא של ההכנסות החודש');
    }
  };

  const handleViewRecommendations = () => {
    if (onChatWithAgent) {
      onChatWithAgent('מרקוס, מה ההצעות שלך לשיפור ההכנסות?');
    }
  };

  if (error) {
    return (
      <BaseWidget
        title="הכנסות חודשיות"
        agent="marcus"
        icon={DollarSign}
      >
        <div className="text-center py-4">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-2" />
          <p className="text-sm text-gray-600">{error}</p>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchRevenue}
            className="mt-2"
          >
            נסה שוב
          </Button>
        </div>
      </BaseWidget>
    );
  }

  if (!revenue) return null;

  const isPositive = revenue.trend === 'up';

  return (
    <BaseWidget
      title="הכנסות חודשיות"
      agent="marcus"
      icon={DollarSign}
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* Main Revenue Display */}
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900">
            {formatCurrency(revenue.thisMonth)}
          </div>
          <div className="text-sm text-gray-500 mt-1">החודש הנוכחי</div>
        </div>

        {/* Trend Indicator */}
        <div className={cn(
          "flex items-center justify-center gap-2 p-3 rounded-lg",
          isPositive ? "bg-green-50" : "bg-red-50"
        )}>
          {isPositive ? (
            <TrendingUp className="w-5 h-5 text-green-600" />
          ) : (
            <TrendingDown className="w-5 h-5 text-red-600" />
          )}
          <span className={cn(
            "text-lg font-semibold",
            isPositive ? "text-green-600" : "text-red-600"
          )}>
            {isPositive ? '+' : ''}{revenue.change.toFixed(1)}%
          </span>
          <span className="text-sm text-gray-600">לעומת חודש שעבר</span>
        </div>

        {/* Comparison */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-gray-600">חודש שעבר</div>
            <div className="font-semibold text-gray-900 mt-1">
              {formatCurrency(revenue.lastMonth)}
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-gray-600">שינוי</div>
            <div className={cn(
              "font-semibold mt-1",
              isPositive ? "text-green-600" : "text-red-600"
            )}>
              {isPositive ? '+' : ''}{formatCurrency(revenue.thisMonth - revenue.lastMonth)}
            </div>
          </div>
        </div>

        {/* Marcus Insight */}
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-bold">💼</span>
            </div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-blue-900 mb-1">
                תובנה של מרקוס:
              </div>
              <div className="text-sm text-blue-800">
                {revenue.insight}
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start gap-2">
            <div className="text-lg">💡</div>
            <div className="flex-1 text-sm text-yellow-900">
              {revenue.recommendation}
            </div>
          </div>
        </div>

        {/* Payment Stats */}
        {revenue.invoiceCount > 0 && (
          <div className="text-xs text-gray-600 text-center">
            {revenue.paidCount} מתוך {revenue.invoiceCount} חשבונות שולמו ({revenue.paymentRate.toFixed(0)}%)
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleViewDetails}
            className="flex-1"
          >
            פירוט מלא
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleViewRecommendations}
            className="flex-1"
          >
            הצעות לשיפור
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}
