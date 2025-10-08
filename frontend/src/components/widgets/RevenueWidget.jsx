import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Revenue Widget - Marcus CFO Agent
 * 
 * Shows revenue overview with trends and insights
 */
export default function RevenueWidget({ onChatWithAgent }) {
  const [revenue, setRevenue] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchRevenue();
  }, []);

  const fetchRevenue = async () => {
    setIsLoading(true);
    try {
      // Fetch real revenue data from Backend/Odoo
      const response = await fetch('/api/v1/dashboard/revenue', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': localStorage.getItem('organization_id') || '1'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setRevenue(data);
      } else {
        // Fallback to mock data
        console.warn('Revenue API failed, using mock data');
        const mockData = {
          thisMonth: 45000,
          lastMonth: 39000,
          change: 15.4,
          trend: 'up',
          insight: 'הכנסות עלו ב-15% לעומת החודש הקודם',
          recommendation: 'מרקוס ממליץ: התמקדו בטיפולים מורכבים - הם מניבים 40% מההכנסות'
        };
        setRevenue(mockData);
      }
    } catch (error) {
      console.error('Error fetching revenue:', error);
      // Fallback to mock data on error
      const mockData = {
        thisMonth: 45000,
        lastMonth: 39000,
        change: 15.4,
        trend: 'up',
        insight: 'הכנסות עלו ב-15% לעומת החודש הקודם',
        recommendation: 'מרקוס ממליץ: התמקדו בטיפולים מורכבים - הם מניבים 40% מההכנסות'
      };
      setRevenue(mockData);
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

  if (!revenue) return null;

  const isPositive = revenue.trend === 'up';

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
            {isPositive ? '+' : ''}{revenue.change}%
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
            <div className="text-sm font-semibold mt-1 text-green-600">
              +{formatCurrency(revenue.thisMonth - revenue.lastMonth)}
            </div>
          </div>
        </div>

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
            onClick={() => onChatWithAgent && onChatWithAgent('Show me detailed revenue breakdown')}
          >
            <DollarSign className="w-3 h-3 mr-1" />
            פירוט מלא
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('What can we do to increase revenue?')}
          >
            <ArrowUpRight className="w-3 h-3 mr-1" />
            הצעות לשיפור
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}
