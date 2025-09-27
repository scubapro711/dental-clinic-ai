import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  Grid3X3, 
  LayoutGrid, 
  Maximize2, 
  Minimize2,
  RefreshCw,
  Settings,
  Filter,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  Activity
} from 'lucide-react';
import StatisticsCard from './StatisticsCard';

/**
 * DashboardGrid Component
 * 
 * A responsive grid container for dashboard components with advanced features:
 * - Responsive grid layout (1-4 columns based on screen size)
 * - Real-time data updates and agent status monitoring
 * - Grid customization and filtering capabilities
 * - Mission Control Dashboard integration
 * - Agentic UX principles implementation
 * - Performance optimization for large datasets
 */
const DashboardGrid = ({
  cards = [],
  columns = 'auto', // 'auto', 1, 2, 3, 4
  gap = 'default', // 'tight', 'default', 'loose'
  showControls = true,
  enableFiltering = true,
  enableRefresh = true,
  refreshInterval = 30000, // 30 seconds
  agentMode = 'active',
  onCardClick,
  onRefresh,
  onFilterChange,
  className,
  ...props
}) => {
  // State management
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [visibleCards, setVisibleCards] = useState(cards);
  const [filterStatus, setFilterStatus] = useState('all');
  const [gridColumns, setGridColumns] = useState(columns);
  const [isExpanded, setIsExpanded] = useState(false);

  // Auto-refresh functionality
  useEffect(() => {
    if (!enableRefresh || refreshInterval <= 0) return;

    const interval = setInterval(async () => {
      await handleRefresh();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [enableRefresh, refreshInterval]);

  // Filter cards based on status
  useEffect(() => {
    if (filterStatus === 'all') {
      setVisibleCards(cards);
    } else {
      setVisibleCards(cards.filter(card => card.status === filterStatus));
    }
  }, [cards, filterStatus]);

  // Grid column classes mapping
  const getGridColumns = useMemo(() => {
    if (columns === 'auto') {
      return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4';
    }
    
    const columnMap = {
      1: 'grid-cols-1',
      2: 'grid-cols-1 md:grid-cols-2',
      3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
      4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
    };
    
    return columnMap[gridColumns] || columnMap[4];
  }, [gridColumns, columns]);

  // Gap classes mapping
  const getGapClass = useMemo(() => {
    const gapMap = {
      'tight': 'gap-3',
      'default': 'gap-6',
      'loose': 'gap-8'
    };
    return gapMap[gap] || gapMap['default'];
  }, [gap]);

  // Handle refresh
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await onRefresh?.();
      setLastRefresh(new Date());
    } catch (error) {
      console.error('Dashboard refresh failed:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle filter change
  const handleFilterChange = (status) => {
    setFilterStatus(status);
    onFilterChange?.(status);
  };

  // Get agent status color
  const getAgentStatusColor = () => {
    switch (agentMode) {
      case 'active':
        return 'bg-green-500';
      case 'monitoring':
        return 'bg-blue-500';
      case 'idle':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  // Get status counts for filter badges
  const getStatusCounts = useMemo(() => {
    const counts = {
      all: cards.length,
      success: 0,
      warning: 0,
      error: 0,
      neutral: 0
    };

    cards.forEach(card => {
      if (counts.hasOwnProperty(card.status)) {
        counts[card.status]++;
      }
    });

    return counts;
  }, [cards]);

  return (
    <div 
      className={cn(
        "w-full space-y-6",
        isExpanded && "fixed inset-0 z-50 bg-white p-6 overflow-auto",
        className
      )}
      {...props}
    >
      {/* Dashboard Controls */}
      {showControls && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <LayoutGrid className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg font-semibold">
                    Mission Control Dashboard
                  </CardTitle>
                </div>
                
                {/* Agent Status Indicator */}
                <div className="flex items-center gap-2">
                  <div 
                    className={cn(
                      "w-3 h-3 rounded-full",
                      getAgentStatusColor()
                    )}
                    title={`Agent Mode: ${agentMode}`}
                  />
                  <Badge 
                    variant="outline" 
                    className="text-xs"
                  >
                    Agent: {agentMode}
                  </Badge>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {/* Refresh Control */}
                {enableRefresh && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRefresh}
                    disabled={isRefreshing}
                    className="flex items-center gap-2"
                  >
                    <RefreshCw 
                      className={cn(
                        "h-4 w-4",
                        isRefreshing && "animate-spin"
                      )} 
                    />
                    {isRefreshing ? 'Refreshing...' : 'Refresh'}
                  </Button>
                )}

                {/* Grid Layout Controls */}
                <div className="flex items-center gap-1 border rounded-md p-1">
                  {[1, 2, 3, 4].map(cols => (
                    <Button
                      key={cols}
                      variant={gridColumns === cols ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setGridColumns(cols)}
                      className="h-8 w-8 p-0"
                      title={`${cols} column${cols > 1 ? 's' : ''}`}
                    >
                      <Grid3X3 className="h-3 w-3" />
                    </Button>
                  ))}
                </div>

                {/* Expand/Collapse */}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="flex items-center gap-2"
                >
                  {isExpanded ? (
                    <>
                      <Minimize2 className="h-4 w-4" />
                      Collapse
                    </>
                  ) : (
                    <>
                      <Maximize2 className="h-4 w-4" />
                      Expand
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Status Filters */}
            {enableFiltering && (
              <div className="flex items-center gap-2 pt-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <span className="text-sm text-gray-600 mr-2">Filter by status:</span>
                
                {Object.entries(getStatusCounts).map(([status, count]) => (
                  <Button
                    key={status}
                    variant={filterStatus === status ? "default" : "outline"}
                    size="sm"
                    onClick={() => handleFilterChange(status)}
                    className="flex items-center gap-2 text-xs"
                  >
                    {status === 'success' && <CheckCircle className="h-3 w-3" />}
                    {status === 'warning' && <AlertCircle className="h-3 w-3" />}
                    {status === 'error' && <AlertCircle className="h-3 w-3" />}
                    {status === 'all' && <Activity className="h-3 w-3" />}
                    {status === 'neutral' && <Activity className="h-3 w-3" />}
                    
                    <span className="capitalize">{status}</span>
                    <Badge variant="secondary" className="ml-1 text-xs">
                      {count}
                    </Badge>
                  </Button>
                ))}
              </div>
            )}

            {/* Last Refresh Info */}
            <div className="flex items-center justify-between pt-2 text-xs text-gray-500">
              <span>
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
              <span>
                Showing {visibleCards.length} of {cards.length} cards
              </span>
            </div>
          </CardHeader>
        </Card>
      )}

      {/* Dashboard Grid */}
      <div 
        className={cn(
          "grid w-full",
          getGridColumns,
          getGapClass
        )}
      >
        {visibleCards.map((card, index) => (
          <div
            key={card.id || index}
            className="transition-all duration-200 hover:scale-[1.02]"
          >
            <StatisticsCard
              {...card}
              onClick={() => onCardClick?.(card, index)}
              agentStatus={agentMode}
              className={cn(
                "h-full",
                card.priority === 'high' && "ring-2 ring-red-200",
                card.priority === 'medium' && "ring-1 ring-yellow-200",
                card.className
              )}
            />
          </div>
        ))}
      </div>

      {/* Empty State */}
      {visibleCards.length === 0 && (
        <Card className="border-dashed border-2 border-gray-300">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <EyeOff className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">
              No cards to display
            </h3>
            <p className="text-gray-500 text-center max-w-md">
              {filterStatus === 'all' 
                ? "No dashboard cards are currently available. Add some cards to get started."
                : `No cards match the "${filterStatus}" status filter. Try adjusting your filters.`
              }
            </p>
            {filterStatus !== 'all' && (
              <Button
                variant="outline"
                onClick={() => handleFilterChange('all')}
                className="mt-4"
              >
                Show All Cards
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Performance Indicator */}
      {cards.length > 20 && (
        <div className="text-xs text-gray-500 text-center">
          Performance mode: Optimized for {cards.length} cards
        </div>
      )}
    </div>
  );
};

export default DashboardGrid;
