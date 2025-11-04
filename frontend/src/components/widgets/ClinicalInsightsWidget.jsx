import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BaseWidget from './BaseWidget';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Activity, AlertTriangle, CheckCircle, Clock, TrendingUp, Eye } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Clinical Insights Widget - Sarah Agent
 * 
 * Shows clinical summary, AI findings, and pending treatments
 */
export default function ClinicalInsightsWidget({ onChatWithAgent }) {
  const navigate = useNavigate();
  const [clinicalData, setClinicalData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchClinicalData();
  }, []);

  const fetchClinicalData = async () => {
    setIsLoading(true);
    try {
      // TODO: Fetch real clinical data from Backend
      // For now, use mock data
      useMockData();
    } catch (error) {
      console.error('Error fetching clinical data:', error);
      useMockData();
    } finally {
      setIsLoading(false);
    }
  };

  const useMockData = () => {
    const mockData = {
      todayPatients: 12,
      aiFlags: 3,
      pendingTreatments: 5,
      criticalCases: 1,
      recentFindings: [
        {
          id: 1,
          patient: 'Alex Cohen',
          finding: 'Deep cavity - Tooth #14',
          severity: 'high',
          aiConfidence: 97,
          action: 'Root canal recommended'
        },
        {
          id: 2,
          patient: 'Sarah Levi',
          finding: 'Early cavity - Tooth #47',
          severity: 'medium',
          aiConfidence: 78,
          action: 'Monitor or preventive filling'
        },
        {
          id: 3,
          patient: 'David Ben',
          finding: 'Gum inflammation - Quadrant 2',
          severity: 'low',
          aiConfidence: 85,
          action: 'Deep cleaning recommended'
        }
      ],
      stats: {
        xraysAnalyzed: 8,
        treatmentsPlanned: 5,
        aiAccuracy: 94
      }
    };
    setClinicalData(mockData);
  };

  if (!clinicalData) return null;

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100 border-red-300';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-300';
      case 'low': return 'text-blue-600 bg-blue-100 border-blue-300';
      default: return 'text-gray-600 bg-gray-100 border-gray-300';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'high': return <AlertTriangle className="w-4 h-4" />;
      case 'medium': return <Clock className="w-4 h-4" />;
      case 'low': return <CheckCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <BaseWidget
      title="תובנות קליניות"
      agent="sarah"
      icon="🩺"
      isLoading={isLoading}
    >
      <div className="space-y-4">
        {/* Stats Overview */}
        <div className="grid grid-cols-4 gap-3">
          <div className="p-3 bg-blue-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-900">
              {clinicalData.todayPatients}
            </div>
            <div className="text-xs text-blue-600 mt-1">חולים היום</div>
          </div>
          <div className="p-3 bg-red-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-900">
              {clinicalData.aiFlags}
            </div>
            <div className="text-xs text-red-600 mt-1">AI Flags</div>
          </div>
          <div className="p-3 bg-yellow-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-yellow-900">
              {clinicalData.pendingTreatments}
            </div>
            <div className="text-xs text-yellow-600 mt-1">טיפולים ממתינים</div>
          </div>
          <div className="p-3 bg-purple-50 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-900">
              {clinicalData.stats.aiAccuracy}%
            </div>
            <div className="text-xs text-purple-600 mt-1">דיוק AI</div>
          </div>
        </div>

        {/* Critical Alert */}
        {clinicalData.criticalCases > 0 && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <div className="flex-1">
                <div className="text-sm font-semibold text-red-900">
                  {clinicalData.criticalCases} מקרה דורש טיפול דחוף
                </div>
                <div className="text-xs text-red-700">
                  בדוק את התור הקליני
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Findings */}
        <div>
          <div className="text-xs font-semibold text-gray-700 mb-2">
            ממצאים אחרונים של Sarah AI:
          </div>
          <div className="space-y-2">
            {clinicalData.recentFindings.map((finding) => (
              <div
                key={finding.id}
                className={cn(
                  'p-3 rounded-lg border-2',
                  getSeverityColor(finding.severity)
                )}
              >
                <div className="flex items-start gap-2">
                  <div className="mt-0.5">
                    {getSeverityIcon(finding.severity)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-sm font-semibold truncate">
                        {finding.patient}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {finding.aiConfidence}% ביטחון
                      </Badge>
                    </div>
                    <div className="text-xs font-medium mb-1">
                      {finding.finding}
                    </div>
                    <div className="text-xs opacity-75">
                      💡 {finding.action}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="text-xs"
                    onClick={() => navigate(`/clinic/clinical?patient=${encodeURIComponent(finding.patient)}`)}
                  >
                    <Eye className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sarah AI Insight */}
        <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <div className="text-lg">🩺</div>
            <div className="flex-1">
              <div className="text-xs font-semibold text-purple-900 mb-1">
                תובנה של Sarah:
              </div>
              <div className="text-xs text-purple-800">
                היום יש {clinicalData.aiFlags} ממצאים שדורשים תשומת לב. 
                המלצה: התחל עם המקרה הקריטי של Alex Cohen.
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
            onClick={() => onChatWithAgent && onChatWithAgent('Show me clinical details')}
          >
            <Activity className="w-3 h-3 mr-1" />
            פירוט מלא
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="flex-1 text-xs"
            onClick={() => onChatWithAgent && onChatWithAgent('What should I prioritize?')}
          >
            <TrendingUp className="w-3 h-3 mr-1" />
            סדר עדיפויות
          </Button>
        </div>
      </div>
    </BaseWidget>
  );
}
