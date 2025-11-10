import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';
import { dashboardService, RevenueData } from '@/services/dashboardService';

/**
 * Revenue Widget - Marcus CFO Agent
 * 
 * Shows revenue overview with trends and insights.
 * Now uses dashboardService for consistent API calls.
 */

interface RevenueWidgetProps {
  onChatWithAgent?: (message: string) => void;
}

export default function RevenueWidget({ onChatWithAgent }: RevenueWidgetProps) {
  const [revenue, setRevenue] = useState<RevenueData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRevenue();
  }, []);

  const fetchRevenue = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get organization ID from localStorage
      const organizationId = localStorage.getItem('current_organization_id') || 
                            localStorage.getItem('organization_id') || 
                            '1';
      
      // Fetch revenue data using dashboard service
      const data = await dashboardService.getRevenue(organizationId);
      setRevenue(data);
    } catch (err) {
      console.error('[RevenueWidget] Error fetching revenue:', err);
      setError('Failed to load revenue data');
      // Service already provides mock data as fallback
    } finally {
      setIsLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0
    }).format(amount);
  };

  if (!revenue) return null;

  const isPositive = revenue.trend === 'up';
  const changeAmount = revenue.thisMonth - revenue.lastMonth;

  return (
    <BaseWidget
      title="הכנסות חודשיות"
      agent="marcus"
      icon="💰"
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* Main Revenue */}
        <div className="text-center">
          <div className="text-3xl font-bold text-gray-900">
            {formatCurrency(revenue.thisMonth)}
          </div>
          <div className="text-xs text-gray-500 mt-1">החודש הנוכחי</div>
        </div>

        {/* Trend */}
        <div className={cn(
          'flex items-center justify-center gap-2 p-3 rounded-lg',
          isPositive ? 'bg-green-100' : 'bg-red-100'
        )}>
          {isPositive ? (
            <TrendingUp className="w-5 h-5 text-green-600" />
          ) : (
            <TrendingDown className="w-5 h-5 text-red-600" />
          )}
          <span className={cn(
            'text-sm font-semibold',
            isPositive ? 'text-green-700' : 'text-red-700'
          )}>
            {isPositive ? '+' : ''}{revenue.change.toFixed(1)}%
          </span>
          <span className="text-xs text-gray-600">
            לעומת חודש שעבר
          </span>
        </div>

        {/* Comparison */}
        <div className="grid grid-cols-2 gap-3 text-center">
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500">חודש שעבר</div>
            <div className="text-sm font-semibold mt-1">
              {formatCurrency(revenue.lastMonth)}
            </div>
          </div>
          <div className="p-2 bg-blue-50 rounded-lg">
            <div className="text-xs text-gray-500">שינוי</div>
            <div className={cn(
              'text-sm font-semibold mt-1',
              isPositive ? 'text-green-600' : 'text-red-600'
            )}>
              {isPositive ? '+' : ''}{formatCurrency(Math.abs(changeAmount))}
            </div>
          </div>
        </div>

        {/* Revenue Breakdown (if available) */}
        {revenue.breakdown && (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-gray-700">פירוט הכנסות:</div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">טיפולים</span>
                <span className="font-semibold">{formatCurrency(revenue.breakdown.treatments)}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">ייעוצים</span>
                <span className="font-semibold">{formatCurrency(revenue.breakdown.consultations)}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-600">אחר</span>
                <span className="font-semibold">{formatCurrency(revenue.breakdown.other)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Insight from Marcus */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <div className="text-lg">💼</div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-blue-900 mb-1">
                תובנה של מרקוס:
              </div>
              <div className="text-xs text-blue-800">
                {revenue.insight}
              </div>
            </div>
          </div>
        </div>

        {/* Recommendation */}
        <div className="bg-green-50 border-2 border-green-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <div className="text-lg">💡</div>
            <div className="flex-1">
              <div className="text-xs text-green-800">
                {revenue.recommendation}
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t">
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent?.('Show me detailed revenue breakdown')}
          >
            <DollarSign className="w-3 h-3 mr-1" />
            פירוט מלא
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent?.('What can we do to increase revenue?')}
          >
            <ArrowUpRight className="w-3 h-3 mr-1" />
            הצעות לשיפור
          </Button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="text-xs text-red-600 text-center">
            {error}
          </div>
        )}
      </div>
    </BaseWidget>
  );
}
