import React, { useState, useEffect } from 'react';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, FileText, Shield, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Transparency Widget
 * 
 * Shows AI decision transparency, audit logs, and explainability
 */
export default function TransparencyWidget({ onChatWithAgent }) {
  const [transparencyData, setTransparencyData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTransparencyData();
  }, []);

  const fetchTransparencyData = async () => {
    setIsLoading(true);
    try {
      // TODO: Fetch real transparency data from Backend
      // For now, use mock data
      useMockData();
    } catch (error) {
      console.error('Error fetching transparency data:', error);
      useMockData();
    } finally {
      setIsLoading(false);
    }
  };

  const useMockData = () => {
    const mockData = {
      recentDecisions: [
        {
          id: 1,
          agent: 'Sarah',
          decision: 'Recommended root canal for tooth #14',
          confidence: 97,
          reasoning: 'X-ray shows deep cavity reaching pulp chamber',
          timestamp: '2 hours ago',
          reviewed: true
        },
        {
          id: 2,
          agent: 'Marcus',
          decision: 'Flagged $5,000 payment anomaly',
          confidence: 85,
          reasoning: 'Payment exceeds typical treatment cost by 40%',
          timestamp: '3 hours ago',
          reviewed: false
        },
        {
          id: 3,
          agent: 'Alex',
          decision: 'Scheduled 3 follow-up appointments',
          confidence: 92,
          reasoning: 'Patient history shows missed appointments',
          timestamp: '5 hours ago',
          reviewed: true
        }
      ],
      auditStats: {
        totalDecisions: 247,
        reviewed: 231,
        flagged: 12,
        overridden: 4
      }
    };
    setTransparencyData(mockData);
  };

  if (!transparencyData) return null;

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <BaseWidget
      title="שקיפות והסברים"
      agent="system"
      icon="👁️"
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* Audit Stats */}
        <div className="grid grid-cols-4 gap-2">
          <div className="p-2 bg-blue-50 rounded text-center">
            <div className="text-lg font-bold text-blue-900">
              {transparencyData.auditStats.totalDecisions}
            </div>
            <div className="text-xs text-blue-600">החלטות</div>
          </div>
          <div className="p-2 bg-green-50 rounded text-center">
            <div className="text-lg font-bold text-green-900">
              {transparencyData.auditStats.reviewed}
            </div>
            <div className="text-xs text-green-600">נבדקו</div>
          </div>
          <div className="p-2 bg-yellow-50 rounded text-center">
            <div className="text-lg font-bold text-yellow-900">
              {transparencyData.auditStats.flagged}
            </div>
            <div className="text-xs text-yellow-600">סומנו</div>
          </div>
          <div className="p-2 bg-red-50 rounded text-center">
            <div className="text-lg font-bold text-red-900">
              {transparencyData.auditStats.overridden}
            </div>
            <div className="text-xs text-red-600">בוטלו</div>
          </div>
        </div>

        {/* Recent Decisions */}
        <div>
          <div className="text-xs font-semibold text-gray-700 mb-2">
            החלטות אחרונות:
          </div>
          <div className="space-y-2">
            {transparencyData.recentDecisions.map((decision) => (
              <div
                key={decision.id}
                className="p-3 bg-white border border-gray-200 rounded-lg"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-semibold text-gray-900">
                        {decision.agent}
                      </span>
                      <Badge
                        variant="outline"
                        className={cn('text-xs', getConfidenceColor(decision.confidence))}
                      >
                        {decision.confidence}% ביטחון
                      </Badge>
                      {decision.reviewed ? (
                        <CheckCircle className="w-3 h-3 text-green-600" />
                      ) : (
                        <AlertTriangle className="w-3 h-3 text-yellow-600" />
                      )}
                    </div>
                    <div className="text-xs text-gray-900 font-medium mb-1">
                      {decision.decision}
                    </div>
                    <div className="text-xs text-gray-500 flex items-start gap-1">
                      <Info className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      <span>{decision.reasoning}</span>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-2 pt-2 border-t border-gray-100">
                  {decision.timestamp}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <Shield className="w-4 h-4 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="text-xs font-semibold text-blue-900 mb-1">
                שקיפות מלאה
              </div>
              <div className="text-xs text-blue-800">
                כל החלטה של AI מתועדת ומוסברת. תוכל לבדוק, לאשר או לבטל כל החלטה.
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
            onClick={() => onChatWithAgent && onChatWithAgent('Show full audit log')}
          >
            <FileText className="w-3 h-3 mr-1" />
            לוג מלא
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('Explain decision details')}
          >
            <Eye className="w-3 h-3 mr-1" />
            הסבר מפורט
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}
