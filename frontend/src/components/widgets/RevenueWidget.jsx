import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, DollarSign, ArrowUpRight, CreditCard, AlertCircle, Award } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Revenue Widget - Marcus CFO Agent
 * 
 * Shows comprehensive revenue and financial health data
 * Now uses ALL available backend revenue functions for maximum value
 */
export default function RevenueWidget({ onChatWithAgent }) {
  const [revenueData, setRevenueData] = useState(null);
  const [financialHealth, setFinancialHealth] = useState(null);
  const [topTreatments, setTopTreatments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchRevenue();
  }, []);

  const fetchRevenue = async () => {
    setIsLoading(true);
    try {
      // Get organization ID
      const organizationId = localStorage.getItem('organization_id') || '1';
      
      // Fetch enriched revenue data from new endpoint
      const response = await fetch('/api/v1/revenue/dashboard', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || localStorage.getItem('access_token')}`,
          'X-Organization-ID': organizationId
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        setRevenueData(data.revenue);
        setFinancialHealth(data.financial_health);
        setTopTreatments(data.top_treatments || []);
      } else {
        // Empty state if API fails
        console.warn('Revenue API failed, showing empty state');
        setRevenueData({
          today: 0,
          this_week: 0,
          this_month: 0,
          last_month: 0,
          this_year: 0,
          last_year: 0
        });
        setFinancialHealth({
          outstanding_amount: 0,
          outstanding_count: 0,
          payment_success_rate: 0,
          average_invoice: 0,
          collection_rate: 0
        });
        setTopTreatments([]);
      }
    } catch (error) {
      console.error('Error fetching revenue:', error);
      // Empty state on error
      setRevenueData({
        today: 0,
        this_week: 0,
        this_month: 0,
        last_month: 0,
        this_year: 0,
        last_year: 0
      });
      setFinancialHealth({
        outstanding_amount: 0,
        outstanding_count: 0,
        payment_success_rate: 0,
        average_invoice: 0,
        collection_rate: 0
      });
      setTopTreatments([]);
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

  if (!revenueData) return null;

  // Calculate month-over-month change
  const monthChange = revenueData.this_month - revenueData.last_month;
  const monthChangePercent = revenueData.last_month > 0 
    ? (monthChange / revenueData.last_month * 100) 
    : 0;
  const isPositive = monthChangePercent > 0;

  // Calculate year-over-year change
  const yearChange = revenueData.this_year - revenueData.last_year;
  const yearChangePercent = revenueData.last_year > 0
    ? (yearChange / revenueData.last_year * 100)
    : 0;

  // Generate insights
  const insight = monthChangePercent > 10
    ? `הכנסות עלו ב-${Math.abs(monthChangePercent).toFixed(1)}% - ביצועים מצוינים! 🎉`
    : monthChangePercent > 0
    ? `הכנסות עלו ב-${Math.abs(monthChangePercent).toFixed(1)}% - צמיחה יפה`
    : monthChangePercent < -10
    ? `הכנסות ירדו ב-${Math.abs(monthChangePercent).toFixed(1)}% - דורש תשומת לב`
    : 'הכנסות יציבות לעומת החודש הקודם';

  const recommendation = monthChangePercent > 10
    ? 'מרקוס ממליץ: המשיכו כך! התמקדו בטיפולים מורכבים'
    : monthChangePercent > 0
    ? 'מרקוס ממליץ: צמיחה טובה. שקלו להגדיל את קיבולת התורים'
    : financialHealth && financialHealth.collection_rate < 85
    ? 'מרקוס ממליץ: שפרו את שיעור הגבייה - פנו למטופלים עם חובות'
    : 'מרקוס ממליץ: בדקו אילו טיפולים פחות רווחיים ושפרו את השיווק';

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
            {formatCurrency(revenueData.this_month)}
          </div>
          <div className="text-xs text-gray-500 mt-1">החודש הנוכחי</div>
        </div>

        {/* Month Trend */}
        <div className={cn(
          'flex items-center justify-center gap-2 p-3 rounded-lg',
          isPositive ? 'bg-green-100' : monthChangePercent < 0 ? 'bg-red-100' : 'bg-gray-100'
        )}>
          {isPositive ? (
            <TrendingUp className="w-5 h-5 text-green-600" />
          ) : monthChangePercent < 0 ? (
            <TrendingDown className="w-5 h-5 text-red-600" />
          ) : (
            <DollarSign className="w-5 h-5 text-gray-600" />
          )}
          <span className={cn(
            'text-sm font-semibold',
            isPositive ? 'text-green-700' : monthChangePercent < 0 ? 'text-red-700' : 'text-gray-700'
          )}>
            {monthChangePercent > 0 ? '+' : ''}{monthChangePercent.toFixed(1)}%
          </span>
          <span className="text-xs text-gray-600">
            לעומת חודש שעבר
          </span>
        </div>

        {/* Time Period Comparison - NEW! */}
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500">היום</div>
            <div className="text-sm font-semibold mt-1">
              {formatCurrency(revenueData.today)}
            </div>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500">השבוע</div>
            <div className="text-sm font-semibold mt-1">
              {formatCurrency(revenueData.this_week)}
            </div>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="text-xs text-gray-500">חודש שעבר</div>
            <div className="text-sm font-semibold mt-1">
              {formatCurrency(revenueData.last_month)}
            </div>
          </div>
          <div className="p-2 bg-blue-50 rounded-lg">
            <div className="text-xs text-gray-500">שינוי</div>
            <div className={cn(
              'text-sm font-semibold mt-1',
              isPositive ? 'text-green-600' : monthChangePercent < 0 ? 'text-red-600' : 'text-gray-600'
            )}>
              {monthChangePercent > 0 ? '+' : ''}{formatCurrency(monthChange)}
            </div>
          </div>
        </div>

        {/* Year Comparison - NEW! */}
        <div className="p-3 bg-purple-50 rounded-lg border-2 border-purple-200">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-gray-600">השנה</div>
              <div className="text-lg font-semibold">{formatCurrency(revenueData.this_year)}</div>
            </div>
            <div className={cn(
              'text-sm font-semibold',
              yearChangePercent > 0 ? 'text-green-600' : 'text-gray-600'
            )}>
              {yearChangePercent > 0 ? '+' : ''}{yearChangePercent.toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Financial Health - NEW! */}
        {financialHealth && (
          <div className="space-y-2">
            <div className="text-xs font-semibold text-gray-700">💳 בריאות פיננסית:</div>
            
            <div className="grid grid-cols-2 gap-2">
              <div className="p-2 bg-green-50 rounded-lg">
                <div className="flex items-center gap-1">
                  <CreditCard className="w-3 h-3 text-green-600" />
                  <div className="text-xs text-gray-600">תשלומים</div>
                </div>
                <div className="text-sm font-semibold text-green-700 mt-1">
                  {financialHealth.payment_success_rate.toFixed(0)}%
                </div>
              </div>
              
              <div className="p-2 bg-blue-50 rounded-lg">
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-blue-600" />
                  <div className="text-xs text-gray-600">גבייה</div>
                </div>
                <div className="text-sm font-semibold text-blue-700 mt-1">
                  {financialHealth.collection_rate.toFixed(0)}%
                </div>
              </div>
            </div>

            {financialHealth.outstanding_count > 0 && (
              <div className="p-2 bg-orange-50 rounded-lg border border-orange-200">
                <div className="flex items-center gap-1">
                  <AlertCircle className="w-3 h-3 text-orange-600" />
                  <div className="text-xs text-orange-800">
                    {formatCurrency(financialHealth.outstanding_amount)} חובות ({financialHealth.outstanding_count} חשבוניות)
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Top Treatments - NEW! */}
        {topTreatments.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1">
              <Award className="w-4 h-4 text-yellow-600" />
              <div className="text-xs font-semibold text-gray-700">טיפולים מובילים:</div>
            </div>
            
            {topTreatments.map((treatment, index) => (
              <div key={index} className="flex items-center justify-between p-2 bg-yellow-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}</span>
                  <div>
                    <div className="text-xs font-semibold">{treatment.name}</div>
                    <div className="text-xs text-gray-600">{treatment.count} טיפולים</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold">{formatCurrency(treatment.revenue)}</div>
                  <div className="text-xs text-gray-600">{treatment.percentage.toFixed(0)}%</div>
                </div>
              </div>
            ))}
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
                {insight}
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
                {recommendation}
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
