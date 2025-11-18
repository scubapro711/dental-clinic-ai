import React, { useState, useEffect } from 'react';
import { toast } from 'sonner';
import BaseWidget from './BaseWidget';
import DecisionCard from './DecisionCard';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Filter,
  SortAsc,
  CheckCircle2,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { dashboardService, Decision } from '@/services/dashboardService';

interface EnhancedDecisionQueueWidgetProps {
  onChatWithAgent?: (message: string) => void;
}

type FilterAgent = 'all' | 'alex' | 'sarah' | 'marcus' | 'sophia' | 'harper';
type FilterPriority = 'all' | 'critical' | 'high' | 'medium' | 'low';
type FilterCategory = 'all' | 'clinical' | 'operational' | 'financial' | 'compliance';
type SortOption = 'priority' | 'newest' | 'oldest';

/**
 * Enhanced Decision Queue Widget
 * 
 * Comprehensive urgent actions center with:
 * - Advanced filtering (agent, priority, category)
 * - Sorting options
 * - Expandable decision cards
 * - Quick actions and batch operations
 * - Real-time updates
 */
export default function EnhancedDecisionQueueWidget({ onChatWithAgent }: EnhancedDecisionQueueWidgetProps) {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [filteredDecisions, setFilteredDecisions] = useState<Decision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');
  
  // Filters
  const [filterAgent, setFilterAgent] = useState<FilterAgent>('all');
  const [filterPriority, setFilterPriority] = useState<FilterPriority>('all');
  const [filterCategory, setFilterCategory] = useState<FilterCategory>('all');
  const [sortBy, setSortBy] = useState<SortOption>('priority');
  
  // UI State
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchDecisions();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDecisions, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Apply filters and sorting whenever decisions or filter state changes
    applyFiltersAndSort();
  }, [decisions, filterAgent, filterPriority, filterCategory, sortBy]);

  const fetchDecisions = async () => {
    setIsLoading(true);
    try {
      const orgId = localStorage.getItem('current_organization_id') || 
                    localStorage.getItem('organization_id') || 
                    '1';
      
      const data = await dashboardService.getDecisionQueue(orgId, 50); // Fetch more for filtering
      setDecisions(data);
    } catch (error) {
      console.error('Error fetching decisions:', error);
      setDecisions([]);
    } finally {
      setIsLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = [...decisions];

    // Apply agent filter
    if (filterAgent !== 'all') {
      filtered = filtered.filter(d => d.agent === filterAgent);
    }

    // Apply priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter(d => d.priority === filterPriority);
    }

    // Apply category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(d => d.category === filterCategory);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      if (sortBy === 'priority') {
        const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        const aPriority = priorityOrder[a.priority] ?? 2;
        const bPriority = priorityOrder[b.priority] ?? 2;
        if (aPriority !== bPriority) {
          return aPriority - bPriority;
        }
        // Secondary sort by timestamp (newest first)
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      } else if (sortBy === 'newest') {
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      } else if (sortBy === 'oldest') {
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      }
      return 0;
    });

    setFilteredDecisions(filtered);
  };

  const handleApprove = async (decision: Decision) => {
    setStatusMessage('מאשר...');
    try {
      await dashboardService.approveDecision(decision.id);
      setStatusMessage('אושר בהצלחה!');
      toast.success(`✅ ${decision.title} אושר בהצלחה!`, {
        description: decision.patient_name ? `מטופל: ${decision.patient_name}` : undefined,
        duration: 4000,
      });
      await fetchDecisions();
      setTimeout(() => setStatusMessage(''), 2000);
    } catch (error) {
      console.error('Error approving decision:', error);
      setStatusMessage('שגיאה באישור');
      toast.error('❌ שגיאה באישור ההחלטה', {
        description: 'אנא נסה שוב או פנה לתמיכה',
        duration: 5000,
      });
      setTimeout(() => setStatusMessage(''), 2000);
    }
  };

  const handleReject = async (decision: Decision) => {
    setStatusMessage('דוחה...');
    try {
      await dashboardService.rejectDecision(decision.id);
      setStatusMessage('נדחה בהצלחה!');
      toast.info(`🚫 ${decision.title} נדחה`, {
        description: decision.patient_name ? `מטופל: ${decision.patient_name}` : undefined,
        duration: 4000,
      });
      await fetchDecisions();
      setTimeout(() => setStatusMessage(''), 2000);
    } catch (error) {
      console.error('Error rejecting decision:', error);
      setStatusMessage('שגיאה בדחייה');
      toast.error('❌ שגיאה בדחיית ההחלטה', {
        description: 'אנא נסה שוב או פנה לתמיכה',
        duration: 5000,
      });
      setTimeout(() => setStatusMessage(''), 2000);
    }
  };

  const handleViewDetails = (decision: Decision) => {
    // Navigate to agent page or open modal
    if (onChatWithAgent) {
      onChatWithAgent(`Tell me more about: ${decision.title}`);
    }
  };

  const getPriorityCounts = () => {
    return {
      critical: decisions.filter(d => d.priority === 'critical').length,
      high: decisions.filter(d => d.priority === 'high').length,
      medium: decisions.filter(d => d.priority === 'medium').length,
      low: decisions.filter(d => d.priority === 'low').length
    };
  };

  const priorityCounts = getPriorityCounts();
  const hasActiveFilters = filterAgent !== 'all' || filterPriority !== 'all' || filterCategory !== 'all';

  return (
    <BaseWidget
      title="תור החלטות"
      agent="system"
      icon="⚡"
      badge={`${decisions.length} ממתינים`}
      isLoading={isLoading}
    >
      {/* Status Message */}
      {statusMessage && (
        <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700 text-center">
          {statusMessage}
        </div>
      )}

      {/* Priority Summary */}
      {decisions.length > 0 && (
        <div className="mb-3 flex gap-2 flex-wrap">
          {priorityCounts.critical > 0 && (
            <Badge variant="destructive" className="text-xs">
              <AlertCircle className="w-3 h-3 mr-1" />
              {priorityCounts.critical} קריטי
            </Badge>
          )}
          {priorityCounts.high > 0 && (
            <Badge className="text-xs bg-orange-100 text-orange-700 border-orange-300">
              {priorityCounts.high} דחוף
            </Badge>
          )}
          {priorityCounts.medium > 0 && (
            <Badge className="text-xs bg-yellow-100 text-yellow-700 border-yellow-300">
              {priorityCounts.medium} בינוני
            </Badge>
          )}
          {priorityCounts.low > 0 && (
            <Badge className="text-xs bg-blue-100 text-blue-700 border-blue-300">
              {priorityCounts.low} נמוך
            </Badge>
          )}
        </div>
      )}

      {/* Filter & Sort Controls */}
      <div className="mb-3 flex gap-2 items-center">
        <Button
          size="sm"
          variant="outline"
          className="text-xs h-7"
          onClick={() => setShowFilters(!showFilters)}
        >
          <Filter className="w-3 h-3 mr-1" />
          סינון {hasActiveFilters && <Badge className="mr-1 h-4 text-xs">פעיל</Badge>}
        </Button>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortOption)}
          className="text-xs h-7 border rounded px-2"
        >
          <option value="priority">לפי עדיפות</option>
          <option value="newest">החדשים ביותר</option>
          <option value="oldest">הישנים ביותר</option>
        </select>

        <Button
          size="sm"
          variant="ghost"
          className="text-xs h-7 mr-auto"
          onClick={fetchDecisions}
        >
          <RefreshCw className="w-3 h-3" />
        </Button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="mb-3 p-3 bg-gray-50 rounded-lg space-y-2">
          {/* Agent Filter */}
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">סוכן:</label>
            <div className="flex gap-2 flex-wrap">
              {(['all', 'alex', 'sarah', 'marcus', 'sophia', 'harper'] as FilterAgent[]).map(agent => (
                <Button
                  key={agent}
                  size="sm"
                  variant={filterAgent === agent ? 'default' : 'outline'}
                  className="text-xs h-6"
                  onClick={() => setFilterAgent(agent)}
                >
                  {agent === 'all' ? 'הכל' : agent}
                </Button>
              ))}
            </div>
          </div>

          {/* Priority Filter */}
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">עדיפות:</label>
            <div className="flex gap-2 flex-wrap">
              {(['all', 'critical', 'high', 'medium', 'low'] as FilterPriority[]).map(priority => (
                <Button
                  key={priority}
                  size="sm"
                  variant={filterPriority === priority ? 'default' : 'outline'}
                  className="text-xs h-6"
                  onClick={() => setFilterPriority(priority)}
                >
                  {priority === 'all' ? 'הכל' : 
                   priority === 'critical' ? 'קריטי' :
                   priority === 'high' ? 'דחוף' :
                   priority === 'medium' ? 'בינוני' : 'נמוך'}
                </Button>
              ))}
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <label className="text-xs font-semibold text-gray-700 block mb-1">קטגוריה:</label>
            <div className="flex gap-2 flex-wrap">
              {(['all', 'clinical', 'operational', 'financial', 'compliance'] as FilterCategory[]).map(category => (
                <Button
                  key={category}
                  size="sm"
                  variant={filterCategory === category ? 'default' : 'outline'}
                  className="text-xs h-6"
                  onClick={() => setFilterCategory(category)}
                >
                  {category === 'all' ? 'הכל' :
                   category === 'clinical' ? 'קליני' :
                   category === 'operational' ? 'תפעולי' :
                   category === 'financial' ? 'פיננסי' : 'ציות'}
                </Button>
              ))}
            </div>
          </div>

          {/* Clear Filters */}
          {hasActiveFilters && (
            <Button
              size="sm"
              variant="ghost"
              className="text-xs h-6 w-full"
              onClick={() => {
                setFilterAgent('all');
                setFilterPriority('all');
                setFilterCategory('all');
              }}
            >
              נקה סינונים
            </Button>
          )}
        </div>
      )}

      {/* Decision List */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {filteredDecisions.length === 0 ? (
          <div className="text-center text-sm text-gray-500 py-8">
            {decisions.length === 0 ? (
              <div>
                <CheckCircle2 className="w-12 h-12 mx-auto mb-2 text-green-500" />
                <p className="font-semibold">כל הכבוד! אין החלטות ממתינות</p>
                <p className="text-xs mt-1">כל המשימות הדחופות טופלו</p>
              </div>
            ) : (
              <div>
                <Filter className="w-12 h-12 mx-auto mb-2 text-gray-400" />
                <p className="font-semibold">אין תוצאות לסינון זה</p>
                <p className="text-xs mt-1">נסה לשנות את הסינונים</p>
              </div>
            )}
          </div>
        ) : (
          filteredDecisions.map((decision) => (
            <DecisionCard
              key={decision.id}
              decision={decision}
              onApprove={handleApprove}
              onReject={handleReject}
              onViewDetails={handleViewDetails}
            />
          ))
        )}
      </div>

      {/* Footer - Showing count */}
      {filteredDecisions.length > 0 && (
        <div className="mt-3 pt-3 border-t text-center">
          <p className="text-xs text-gray-600">
            מציג {filteredDecisions.length} מתוך {decisions.length} החלטות
          </p>
        </div>
      )}
    </BaseWidget>
  );
}
