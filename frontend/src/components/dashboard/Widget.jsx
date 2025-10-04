/**
 * Widget - Base component for all dashboard widgets
 * 
 * Features:
 * - Consistent header with title and icon
 * - Menu with common actions (refresh, fullscreen, configure, remove)
 * - Loading, error, and empty states
 * - Responsive design
 */

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  MoreVertical,
  RefreshCw,
  Maximize2,
  Settings,
  X,
  Loader2,
  AlertCircle,
  Inbox,
} from 'lucide-react'
import { cn } from '@/lib/utils'

export function Widget({
  id,
  title,
  icon: Icon,
  children,
  loading = false,
  error = null,
  empty = false,
  emptyMessage = 'No data available',
  onRefresh,
  onFullscreen,
  onConfigure,
  onRemove,
  className,
  headerClassName,
  contentClassName,
}) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    if (onRefresh && !isRefreshing) {
      setIsRefreshing(true)
      try {
        await onRefresh()
      } finally {
        setIsRefreshing(false)
      }
    }
  }

  return (
    <Card className={cn('h-full flex flex-col', className)}>
      <CardHeader className={cn('flex flex-row items-center justify-between space-y-0 pb-2', headerClassName)}>
        <CardTitle className="flex items-center gap-2 text-base font-semibold">
          {Icon && <Icon className="h-4 w-4" />}
          {title}
        </CardTitle>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {onRefresh && (
              <DropdownMenuItem onClick={handleRefresh} disabled={isRefreshing}>
                <RefreshCw className={cn('mr-2 h-4 w-4', isRefreshing && 'animate-spin')} />
                Refresh
              </DropdownMenuItem>
            )}
            {onFullscreen && (
              <DropdownMenuItem onClick={onFullscreen}>
                <Maximize2 className="mr-2 h-4 w-4" />
                Fullscreen
              </DropdownMenuItem>
            )}
            {onConfigure && (
              <DropdownMenuItem onClick={onConfigure}>
                <Settings className="mr-2 h-4 w-4" />
                Configure
              </DropdownMenuItem>
            )}
            {onRemove && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onRemove} className="text-destructive">
                  <X className="mr-2 h-4 w-4" />
                  Remove
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </CardHeader>

      <CardContent className={cn('flex-1 overflow-auto', contentClassName)}>
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">Loading...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <AlertCircle className="h-8 w-8 mx-auto mb-2 text-destructive" />
              <p className="text-sm font-medium">Error loading data</p>
              <p className="text-xs text-muted-foreground mt-1">{error}</p>
              {onRefresh && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRefresh}
                  className="mt-4"
                >
                  Try Again
                </Button>
              )}
            </div>
          </div>
        ) : empty ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <Inbox className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">{emptyMessage}</p>
            </div>
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Widget with custom header (no card wrapper)
 */
export function WidgetRaw({
  id,
  title,
  icon: Icon,
  children,
  onRefresh,
  onFullscreen,
  onConfigure,
  onRemove,
  className,
}) {
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    if (onRefresh && !isRefreshing) {
      setIsRefreshing(true)
      try {
        await onRefresh()
      } finally {
        setIsRefreshing(false)
      }
    }
  }

  return (
    <div className={cn('h-full flex flex-col', className)}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="flex items-center gap-2 text-lg font-semibold">
          {Icon && <Icon className="h-5 w-5" />}
          {title}
        </h3>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {onRefresh && (
              <DropdownMenuItem onClick={handleRefresh} disabled={isRefreshing}>
                <RefreshCw className={cn('mr-2 h-4 w-4', isRefreshing && 'animate-spin')} />
                Refresh
              </DropdownMenuItem>
            )}
            {onFullscreen && (
              <DropdownMenuItem onClick={onFullscreen}>
                <Maximize2 className="mr-2 h-4 w-4" />
                Fullscreen
              </DropdownMenuItem>
            )}
            {onConfigure && (
              <DropdownMenuItem onClick={onConfigure}>
                <Settings className="mr-2 h-4 w-4" />
                Configure
              </DropdownMenuItem>
            )}
            {onRemove && (
              <>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onRemove} className="text-destructive">
                  <X className="mr-2 h-4 w-4" />
                  Remove
                </DropdownMenuItem>
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  )
}
