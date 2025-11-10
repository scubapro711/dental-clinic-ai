# Dashboard Architecture Design

## Date: 2025-10-31

## Overview
Professional SaaS dashboard with fixed right sidebar, drag-and-drop widgets, resize functionality, and full backend integration for multi-tenant architecture.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Header (DashboardHeader)                                   │
│  - Logo, User Info, Actions                                 │
└─────────────────────────────────────────────────────────────┘
┌──────────────────────────────┬──────────────────────────────┐
│                              │                              │
│  Main Content Area           │  Fixed Right Sidebar         │
│  (GridLayout)                │  (DashboardSidebar)          │
│                              │                              │
│  ┌────────┐  ┌────────┐     │  ┌────────────────────────┐  │
│  │Widget A│  │Widget B│     │  │  Widget Library        │  │
│  │        │  │        │     │  │  ┌──────────────────┐  │  │
│  └────────┘  └────────┘     │  │  │ 📊 Today's Pts   │  │  │
│                              │  │  ├──────────────────┤  │  │
│  ┌────────────────────┐     │  │  │ 📈 Revenue       │  │  │
│  │Widget C            │     │  │  ├──────────────────┤  │  │
│  │  (Draggable &      │     │  │  │ ⚙️  Compliance   │  │  │
│  │   Resizable)       │     │  │  └──────────────────┘  │  │
│  └────────────────────┘     │  │                        │  │
│                              │  │  Navigation            │  │
│                              │  │  ┌──────────────────┐  │  │
│                              │  │  │ 🏠 Dashboard     │  │  │
│                              │  │  ├──────────────────┤  │  │
│                              │  │  │ 📅 Schedule      │  │  │
│                              │  │  ├──────────────────┤  │  │
│                              │  │  │ 👥 Patients      │  │  │
│                              │  │  └──────────────────┘  │  │
│                              │  └────────────────────────┘  │
│                              │                              │
└──────────────────────────────┴──────────────────────────────┘
```

---

## Component Structure

```
src/
├── components/
│   ├── dashboard/
│   │   ├── DashboardLayout.tsx         # Main layout wrapper
│   │   ├── DashboardHeader.tsx         # Top header (existing, updated)
│   │   ├── DashboardSidebar.tsx        # NEW: Fixed right sidebar
│   │   ├── DashboardGrid.tsx           # NEW: Grid layout wrapper
│   │   ├── WidgetContainer.tsx         # NEW: Base widget wrapper
│   │   └── widgets/
│   │       ├── index.ts                # Widget registry
│   │       ├── TodaysPatientsWidget.tsx
│   │       ├── RevenueWidget.tsx
│   │       ├── ComplianceWidget.tsx
│   │       ├── DecisionQueueWidget.tsx
│   │       ├── ClinicalWidget.tsx
│   │       ├── FineTuningWidget.tsx
│   │       ├── AgentActivityWidget.tsx
│   │       └── TransparencyWidget.tsx
│   └── ...
├── contexts/
│   ├── DashboardContext.tsx            # Updated: Add grid layout state
│   └── ...
├── hooks/
│   ├── useDashboardLayout.ts           # NEW: Layout management
│   ├── useWidgetData.ts                # NEW: Widget data fetching
│   └── ...
├── pages/
│   └── AgenticDashboard.jsx            # Updated: New layout
└── styles/
    ├── design-system.css               # Existing
    └── dashboard-grid.css              # NEW: Grid-specific styles
```

---

## Data Flow

### 1. Layout State Management

```typescript
interface LayoutItem {
  i: string;           // Widget ID
  x: number;           // X position (grid units)
  y: number;           // Y position (grid units)
  w: number;           // Width (grid units)
  h: number;           // Height (grid units)
  minW?: number;       // Minimum width
  maxW?: number;       // Maximum width
  minH?: number;       // Minimum height
  maxH?: number;       // Maximum height
  static?: boolean;    // Cannot be moved/resized
}

interface DashboardLayout {
  userId: string;
  organizationId: string;
  layouts: {
    lg: LayoutItem[];
    md: LayoutItem[];
    sm: LayoutItem[];
    xs: LayoutItem[];
  };
  widgets: string[];   // Active widget IDs
}
```

### 2. Widget Registry

```typescript
interface WidgetDefinition {
  id: string;
  title: string;
  icon: ReactNode;
  component: React.ComponentType;
  defaultSize: { w: number; h: number };
  minSize?: { w: number; h: number };
  maxSize?: { w: number; h: number };
  category: 'analytics' | 'operations' | 'clinical' | 'admin';
  permissions?: string[];
}

const WIDGET_REGISTRY: Record<string, WidgetDefinition> = {
  'todays-patients': {
    id: 'todays-patients',
    title: "Today's Patients",
    icon: <Users />,
    component: TodaysPatientsWidget,
    defaultSize: { w: 4, h: 2 },
    category: 'operations',
  },
  // ... more widgets
};
```

### 3. Backend API

```typescript
// GET /api/dashboard/layout?userId=X&organizationId=Y
// Response:
{
  userId: "user123",
  organizationId: "org456",
  layouts: {
    lg: [...],
    md: [...],
    sm: [...],
    xs: [...]
  },
  widgets: ["todays-patients", "revenue", "compliance"],
  createdAt: "2025-10-31T...",
  updatedAt: "2025-10-31T..."
}

// POST /api/dashboard/layout
// Request:
{
  userId: "user123",
  organizationId: "org456",
  layouts: { ... },
  widgets: [...]
}

// GET /api/widgets
// Response: List of available widgets with permissions

// GET /api/widgets/:widgetId/data?userId=X&organizationId=Y
// Response: Widget-specific data
```

---

## State Management

### DashboardContext (Updated)

```typescript
interface DashboardContextValue {
  // Existing
  isEditMode: boolean;
  toggleEditMode: () => void;
  isCollapsed: (widgetId: string) => boolean;
  toggleCollapse: (widgetId: string) => void;
  canViewWidget: (widgetId: string) => boolean;
  resetToDefaults: () => void;
  
  // NEW: Grid Layout
  layout: LayoutItem[];
  setLayout: (layout: LayoutItem[]) => void;
  layouts: Record<string, LayoutItem[]>;
  setLayouts: (layouts: Record<string, LayoutItem[]>) => void;
  
  // NEW: Widget Management
  activeWidgets: string[];
  addWidget: (widgetId: string) => void;
  removeWidget: (widgetId: string) => void;
  availableWidgets: WidgetDefinition[];
  
  // NEW: Sidebar
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  
  // NEW: Persistence
  saveLayout: () => Promise<void>;
  loadLayout: () => Promise<void>;
  isSaving: boolean;
  isLoading: boolean;
}
```

---

## Responsive Breakpoints

```typescript
const BREAKPOINTS = {
  lg: 1200,  // Desktop
  md: 996,   // Tablet landscape
  sm: 768,   // Tablet portrait
  xs: 480,   // Mobile landscape
  xxs: 0     // Mobile portrait
};

const COLS = {
  lg: 12,
  md: 10,
  sm: 6,
  xs: 4,
  xxs: 2
};

const ROW_HEIGHT = 60; // pixels
const MARGIN = [16, 16]; // [horizontal, vertical] in pixels
```

---

## Widget Lifecycle

### 1. Widget Registration
```typescript
// widgets/index.ts
export const WIDGETS = {
  'todays-patients': TodaysPatientsWidget,
  'revenue': RevenueWidget,
  // ...
};

export const WIDGET_CONFIGS: Record<string, WidgetDefinition> = {
  'todays-patients': {
    id: 'todays-patients',
    title: "Today's Patients",
    icon: <Users />,
    component: TodaysPatientsWidget,
    defaultSize: { w: 4, h: 2 },
    minSize: { w: 2, h: 2 },
    category: 'operations',
  },
  // ...
};
```

### 2. Widget Rendering
```typescript
// DashboardGrid.tsx
<ResponsiveGridLayout
  layouts={layouts}
  onLayoutChange={handleLayoutChange}
  {...gridProps}
>
  {activeWidgets.map(widgetId => {
    const Widget = WIDGETS[widgetId];
    return (
      <div key={widgetId}>
        <WidgetContainer widgetId={widgetId}>
          <Widget />
        </WidgetContainer>
      </div>
    );
  })}
</ResponsiveGridLayout>
```

### 3. Widget Data Fetching
```typescript
// widgets/TodaysPatientsWidget.tsx
function TodaysPatientsWidget() {
  const { userId, organizationId } = useAuth();
  const { data, isLoading } = useQuery({
    queryKey: ['widget-data', 'todays-patients', userId, organizationId],
    queryFn: () => fetchWidgetData('todays-patients', userId, organizationId)
  });
  
  if (isLoading) return <WidgetSkeleton />;
  
  return (
    <div className="widget-content">
      {/* Widget UI */}
    </div>
  );
}
```

---

## Sidebar Features

### Widget Library Section
- Display all available widgets
- Filter by category
- Search widgets
- Drag to add to dashboard
- Show widget preview on hover

### Navigation Section
- Dashboard (current)
- Schedule
- Patients
- Settings
- Logout

### Collapse/Expand
- Toggle button at top
- Persist state in localStorage
- Smooth animation

---

## Grid Layout Features

### Drag & Drop
- Drag widgets to reorder
- Drag from sidebar to add
- Visual placeholder during drag
- Snap to grid

### Resize
- Resize handles on all corners
- Min/max size constraints
- Maintain aspect ratio (optional)
- Visual feedback during resize

### Responsive
- Auto-adjust on breakpoint change
- Different layouts per breakpoint
- Smooth transitions

### Persistence
- Auto-save on layout change (debounced)
- Save to backend per user+org
- Load on mount
- Reset to defaults option

---

## Styling Strategy

### CSS Variables (design-system.css)
```css
:root {
  --sidebar-width: 280px;
  --sidebar-width-collapsed: 60px;
  --grid-gap: 16px;
  --widget-border-radius: var(--radius-lg);
  --widget-shadow: var(--shadow-md);
}
```

### Grid-Specific Styles (dashboard-grid.css)
```css
.react-grid-layout {
  position: relative;
  transition: height var(--transition-base);
}

.react-grid-item {
  transition: all var(--transition-base);
  background: var(--background);
  border-radius: var(--widget-border-radius);
  box-shadow: var(--widget-shadow);
}

.react-grid-item.react-grid-placeholder {
  background: var(--primary);
  opacity: 0.2;
  border-radius: var(--widget-border-radius);
}

.react-grid-item.resizing {
  opacity: 0.9;
  z-index: 100;
}

.react-grid-item.static {
  cursor: default;
}

.react-resizable-handle {
  background-color: var(--primary);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.react-grid-item:hover .react-resizable-handle {
  opacity: 1;
}
```

---

## Performance Optimizations

### 1. Memoization
```typescript
const MemoizedWidget = React.memo(WidgetComponent);

const children = useMemo(() => {
  return activeWidgets.map(widgetId => (
    <div key={widgetId}>
      <MemoizedWidget widgetId={widgetId} />
    </div>
  ));
}, [activeWidgets]);
```

### 2. Debounced Save
```typescript
const debouncedSave = useMemo(
  () => debounce((layout) => saveLayout(layout), 1000),
  []
);

const handleLayoutChange = (newLayout) => {
  setLayout(newLayout);
  debouncedSave(newLayout);
};
```

### 3. Lazy Loading
```typescript
const TodaysPatientsWidget = lazy(() => import('./widgets/TodaysPatientsWidget'));
const RevenueWidget = lazy(() => import('./widgets/RevenueWidget'));
```

### 4. Virtual Scrolling (if many widgets)
```typescript
// Use react-window or react-virtualized for large widget lists in sidebar
```

---

## Security & RBAC

### Widget Permissions
```typescript
function canViewWidget(widgetId: string, userRole: string): boolean {
  const widget = WIDGET_CONFIGS[widgetId];
  if (!widget.permissions) return true;
  return widget.permissions.includes(userRole);
}

// In DashboardGrid
const visibleWidgets = activeWidgets.filter(widgetId => 
  canViewWidget(widgetId, userRole)
);
```

### API Security
- JWT authentication
- User ID + Org ID validation
- Rate limiting on save endpoint
- Input validation on layout data

---

## Testing Strategy

### Unit Tests
- Widget components
- Layout calculations
- Permission checks
- Data transformations

### Integration Tests
- Drag & drop functionality
- Resize functionality
- Save/load layout
- Add/remove widgets

### E2E Tests
- Full user flow
- Multi-tenant scenarios
- Responsive behavior
- Error handling

---

## Migration Plan

### Phase 1: Setup (Current)
- ✅ Install react-grid-layout
- ✅ Design architecture
- Create base components

### Phase 2: Sidebar
- Create DashboardSidebar component
- Add widget library
- Implement navigation
- Add collapse/expand

### Phase 3: Grid
- Create DashboardGrid component
- Integrate react-grid-layout
- Implement drag & drop
- Add resize functionality

### Phase 4: Widgets
- Refactor existing widgets
- Create WidgetContainer
- Implement widget registry
- Add widget data fetching

### Phase 5: Backend
- Create API endpoints
- Implement save/load
- Add multi-tenant support
- Test with real data

### Phase 6: Polish
- Add animations
- Implement loading states
- Error handling
- Performance optimization

---

## Success Metrics

- ✅ Drag & drop works smoothly (< 16ms frame time)
- ✅ Resize works on all corners
- ✅ Layout persists across sessions
- ✅ Multi-tenant isolation works
- ✅ Responsive on all breakpoints
- ✅ All tests pass
- ✅ No console errors
- ✅ Lighthouse score > 90

---

## Next Steps

1. Create DashboardSidebar component
2. Create DashboardGrid component
3. Update DashboardLayout to use new components
4. Refactor existing widgets
5. Implement backend API
6. Test and deploy

