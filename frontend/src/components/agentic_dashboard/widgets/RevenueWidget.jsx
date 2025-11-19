/**
 * RevenueWidget Component
 * 
 * Displays revenue metrics and trends.
 * Integrated with real backend API.
 */

import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, DollarSign, AlertTriangle } from 'lucide-react';
import { dashboardApiClient } from '../../../utils/dashboardApiClient';

export const RevenueWidget = () => {
  const [revenue, setRevenue] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRevenue = async () => {
      try {
        const data = await dashboardApiClient.get('/revenue/dashboard');
        setRevenue(data);
      } catch (err) {
        console.error('Failed to fetch revenue:', err);
        setError(err.response?.data?.detail || 'שגיאה בטעינת נתוני הכנסות');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRevenue();
  }, []);

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (error || !revenue) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900 dark:text-red-200">שגיאה בטעינת נתונים</p>
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  // Provide default values for undefined fields
  const revenueThisMonth = revenue.revenue_this_month ?? 0;
  const revenueLastMonth = revenue.revenue_last_month ?? 0;
  const outstandingBalance = revenue.outstanding_balance ?? 0;

  const change = revenueThisMonth - revenueLastMonth;
  const changePercent = revenueLastMonth > 0 
    ? ((change / revenueLastMonth) * 100).toFixed(1)
    : '0';
  const isPositive = change >= 0;

  return (
    <div className="p-6">
      {/* This Month Revenue */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <DollarSign className="w-5 h-5 text-emerald-600" />
          <span className="text-sm text-slate-600 dark:text-slate-400">הכנסות החודש</span>
        </div>
        <div className="text-3xl font-bold text-slate-900 dark:text-white mb-1">
          ₪{revenueThisMonth.toLocaleString()}
        </div>
        <div className="flex items-center gap-1">
          {isPositive ? (
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          ) : (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <span className={`text-sm font-bold ${isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
            {isPositive ? '+' : ''}{changePercent}%
          </span>
          <span className="text-xs text-slate-500 dark:text-slate-400">מהחודש שעבר</span>
        </div>
      </div>

      {/* Outstanding Balance */}
      <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-600 dark:text-slate-400">יתרה לגביה</span>
          <span className="text-lg font-bold text-orange-600">
            ₪{outstandingBalance.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Monthly Trend (Mini Chart) */}
      {revenue.monthly_trend && revenue.monthly_trend.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
          <div className="text-xs text-slate-600 dark:text-slate-400 mb-2">מגמה חודשית</div>
          <div className="flex items-end gap-1 h-16">
            {revenue.monthly_trend.map((month, i) => {
              const maxRevenue = Math.max(...revenue.monthly_trend.map(m => m.revenue));
              const height = (month.revenue / maxRevenue) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full bg-emerald-100 dark:bg-emerald-900/20 rounded-t overflow-hidden flex items-end" style={{ height: '48px' }}>
                    <div
                      className="w-full bg-emerald-600 transition-all"
                      style={{ height: `${height}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {month.month.slice(0, 3)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
