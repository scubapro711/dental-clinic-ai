/**
 * Analytics Widget - Financial insights from Marcus (CFO Agent)
 * 
 * Architecture:
 * - Display: Widget → API → Database (direct for basic metrics)
 * - AI Insights: Widget → API → LangGraph → Marcus Agent → Tools
 * 
 * Displays:
 * - Revenue overview (today, this month)
 * - Payment status
 * - Outstanding invoices
 * - Top treatments by revenue
 * - "Ask Marcus" button for AI-powered financial insights
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DollarSign, TrendingUp, TrendingDown, AlertCircle, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"

export function AnalyticsWidget() {
  const [metrics, setMetrics] = useState({
    revenue_today: 0,
    revenue_this_month: 0,
    outstanding_payments: 0,
    payment_success_rate: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // Ask Marcus dialog
  const [askDialog, setAskDialog] = useState({
    open: false,
    question: '',
    loading: false,
    response: null
  })

  useEffect(() => {
    loadMetrics()
    
    // Refresh every 60 seconds
    const interval = setInterval(loadMetrics, 60000)
    return () => clearInterval(interval)
  }, [])

  const loadMetrics = async () => {
    try {
      // Architecture: Widget → API → Database (direct)
      const data = await api.getDashboardMetrics()
      
      setMetrics({
        revenue_today: data.revenue_today || 0,
        revenue_this_month: data.revenue_this_month || 0,
        outstanding_payments: data.outstanding_payments || 0,
        payment_success_rate: data.payment_success_rate || 0,
      })
      
      setError(null)
      console.log('[AnalyticsWidget] Loaded financial metrics:', data)
    } catch (err) {
      console.error('Error loading analytics:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleAskMarcus = () => {
    setAskDialog({
      open: true,
      question: '',
      loading: false,
      response: null
    })
  }

  const submitQuestion = async () => {
    if (!askDialog.question.trim()) {
      alert('Please enter a question')
      return
    }

    setAskDialog({ ...askDialog, loading: true, response: null })

    try {
      // Architecture: Widget → API → LangGraph → Marcus Agent
      // Send natural language question to Marcus
      const response = await api.sendMessage(askDialog.question)
      
      setAskDialog({
        ...askDialog,
        loading: false,
        response: response.response
      })
      
      console.log('[AnalyticsWidget] Marcus response:', response)
    } catch (err) {
      console.error('Error asking Marcus:', err)
      setAskDialog({
        ...askDialog,
        loading: false,
        response: `Error: ${err.message}`
      })
    }
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const formatPercent = (value) => {
    return `${value.toFixed(1)}%`
  }

  return (
    <>
      <Widget
        id="analytics"
        title="Financial Analytics"
        icon={DollarSign}
        loading={loading}
        error={error}
        onRefresh={loadMetrics}
        actions={
          <Button
            variant="outline"
            size="sm"
            onClick={handleAskMarcus}
            className="h-7 text-xs"
          >
            <MessageSquare className="h-3 w-3 mr-1" />
            Ask Marcus
          </Button>
        }
      >
        <div className="space-y-4">
          {/* Revenue Cards */}
          <div className="grid grid-cols-2 gap-3">
            {/* Today's Revenue */}
            <div className="p-3 border rounded-lg bg-gradient-to-br from-green-50 to-white">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">Today</span>
                <TrendingUp className="h-3 w-3 text-green-600" />
              </div>
              <p className="text-lg font-bold text-green-700">
                {formatCurrency(metrics.revenue_today)}
              </p>
              <p className="text-xs text-muted-foreground">Revenue</p>
            </div>

            {/* This Month's Revenue */}
            <div className="p-3 border rounded-lg bg-gradient-to-br from-blue-50 to-white">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-muted-foreground">This Month</span>
                <TrendingUp className="h-3 w-3 text-blue-600" />
              </div>
              <p className="text-lg font-bold text-blue-700">
                {formatCurrency(metrics.revenue_this_month)}
              </p>
              <p className="text-xs text-muted-foreground">Revenue</p>
            </div>
          </div>

          {/* Payment Metrics */}
          <div className="space-y-2">
            {/* Outstanding Payments */}
            <div className="flex items-center justify-between p-2 border rounded-lg">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-orange-600" />
                <span className="text-sm font-medium">Outstanding</span>
              </div>
              <Badge variant="secondary" className="text-orange-700 bg-orange-100">
                {metrics.outstanding_payments} invoices
              </Badge>
            </div>

            {/* Payment Success Rate */}
            <div className="flex items-center justify-between p-2 border rounded-lg">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <span className="text-sm font-medium">Success Rate</span>
              </div>
              <span className="text-sm font-bold text-green-700">
                {formatPercent(metrics.payment_success_rate)}
              </span>
            </div>
          </div>

          {/* Quick Insights */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start gap-2">
              <DollarSign className="h-4 w-4 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs font-medium text-blue-900 mb-1">
                  Financial Insights
                </p>
                <p className="text-xs text-blue-700">
                  {metrics.revenue_this_month > 50000
                    ? "Strong month! Revenue is above target."
                    : "Revenue is below target. Consider reviewing pricing or increasing appointments."}
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  {metrics.outstanding_payments > 10
                    ? `${metrics.outstanding_payments} outstanding invoices need attention.`
                    : "Payment collection is on track."}
                </p>
              </div>
            </div>
          </div>

          {/* Ask Marcus CTA */}
          <Button
            variant="default"
            className="w-full"
            onClick={handleAskMarcus}
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Ask Marcus for Financial Insights
          </Button>
        </div>
      </Widget>

      {/* Ask Marcus Dialog */}
      <Dialog open={askDialog.open} onOpenChange={(open) => setAskDialog({ ...askDialog, open })}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Ask Marcus (CFO Agent)</DialogTitle>
            <DialogDescription>
              Ask any financial question and Marcus will analyze the data to provide insights.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Question Input */}
            <div className="space-y-2">
              <Textarea
                placeholder="Example: What's our revenue trend this month? Which treatments are most profitable?"
                value={askDialog.question}
                onChange={(e) => setAskDialog({ ...askDialog, question: e.target.value })}
                rows={3}
                disabled={askDialog.loading}
              />
            </div>

            {/* Suggested Questions */}
            {!askDialog.response && (
              <div className="space-y-2">
                <p className="text-xs text-muted-foreground">Suggested questions:</p>
                <div className="flex flex-wrap gap-2">
                  {[
                    "What's our revenue this month?",
                    "Which treatments are most profitable?",
                    "How many outstanding invoices do we have?",
                    "What's our payment collection rate?",
                    "Show me financial trends for the last 30 days"
                  ].map((suggestion) => (
                    <Button
                      key={suggestion}
                      variant="outline"
                      size="sm"
                      className="text-xs h-7"
                      onClick={() => setAskDialog({ ...askDialog, question: suggestion })}
                      disabled={askDialog.loading}
                    >
                      {suggestion}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Response */}
            {askDialog.response && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-2 mb-2">
                  <DollarSign className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">Marcus says:</p>
                  </div>
                </div>
                <div className="text-sm text-blue-800 whitespace-pre-wrap">
                  {askDialog.response}
                </div>
              </div>
            )}

            {/* Loading */}
            {askDialog.loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-3 text-sm text-muted-foreground">Marcus is analyzing...</span>
              </div>
            )}
          </div>

          <DialogFooter>
            {!askDialog.response ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => setAskDialog({ open: false, question: '', loading: false, response: null })}
                  disabled={askDialog.loading}
                >
                  Cancel
                </Button>
                <Button
                  onClick={submitQuestion}
                  disabled={askDialog.loading || !askDialog.question.trim()}
                >
                  {askDialog.loading ? 'Analyzing...' : 'Ask Marcus'}
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => setAskDialog({ ...askDialog, question: '', response: null })}
                >
                  Ask Another Question
                </Button>
                <Button
                  onClick={() => setAskDialog({ open: false, question: '', loading: false, response: null })}
                >
                  Close
                </Button>
              </>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
