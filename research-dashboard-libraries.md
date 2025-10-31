# Dashboard Libraries & Components Research

## Date: 2025-10-31

## Goal
Build a professional SaaS dashboard with:
- Fixed right sidebar
- Drag-and-drop widgets
- Resize functionality
- Backend integration for multi-tenant architecture

---

## 1. Grid Layout Library: react-grid-layout ✅

**GitHub:** https://github.com/react-grid-layout/react-grid-layout
**NPM:** `react-grid-layout`
**Stars:** High popularity
**Used by:** Grafana, Kibana, AWS CloudFront, HubSpot, BitMEX, Metabase

### Features
- ✅ **Drag & Drop** - Built-in draggable widgets
- ✅ **Resize** - Resizable widgets with handles (all corners supported)
- ✅ **Responsive** - Breakpoint support (lg, md, sm, xs, xxs)
- ✅ **Save/Load Layout** - Serializable layout state
- ✅ **Add/Remove Widgets** - Dynamic widget management
- ✅ **Static Widgets** - Lock specific widgets
- ✅ **Min/Max Constraints** - Per-widget size limits
- ✅ **Bounded Layout** - Keep widgets within container
- ✅ **Collision Prevention** - Prevent overlapping
- ✅ **CSS Transforms** - High performance (6x faster)
- ✅ **React 16+ Compatible**

### Key Components
```javascript
import GridLayout from "react-grid-layout";
import { Responsive as ResponsiveGridLayout, WidthProvider } from "react-grid-layout";

const ResponsiveGridLayout = WidthProvider(Responsive);
```

### Layout Structure
```javascript
const layout = [
  { i: "widget-1", x: 0, y: 0, w: 2, h: 2 },
  { i: "widget-2", x: 2, y: 0, w: 2, h: 1, minW: 2, maxW: 4 },
  { i: "widget-3", x: 0, y: 2, w: 1, h: 1, static: true }
];
```

### Responsive Breakpoints
```javascript
breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
```

### Callbacks
- `onLayoutChange(layout)` - Save layout after drag/resize
- `onDragStart`, `onDrag`, `onDragStop`
- `onResizeStart`, `onResize`, `onResizeStop`
- `onDrop` - Drop from outside
- `onBreakpointChange` - Responsive breakpoint changes

### Examples Available
1. Showcase - Full demo
2. Basic - Simple grid
3. LocalStorage - Save/load layout
4. Responsive LocalStorage - Save per breakpoint
5. Dynamic Add/Remove - Widget management
6. Toolbox - Drag from sidebar
7. Drag From Outside - External elements
8. Min/Max Width/Height - Constraints
9. Prevent Collision - No overlap

### Installation
```bash
npm install react-grid-layout
```

### CSS Required
```javascript
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
```

---

## 2. Sidebar Component: react-pro-sidebar ✅

**GitHub:** https://github.com/azouaoui-med/react-pro-sidebar
**NPM:** `react-pro-sidebar`

### Features
- ✅ **Customizable** - Full control over appearance
- ✅ **Responsive** - Mobile-friendly
- ✅ **Collapsible** - Toggle sidebar
- ✅ **Icons Support** - Material-UI icons integration
- ✅ **Menu Items** - Nested menus
- ✅ **RTL Support** - Right-to-left languages

### Alternative: Shadcn UI Sidebar ✅
**URL:** https://ui.shadcn.com/docs/components/sidebar

### Features
- ✅ **Modern Design** - Tailwind CSS based
- ✅ **Collapsible State** - Built-in state management
- ✅ **Composable** - Multiple sidebar parts
- ✅ **Accessible** - ARIA compliant

---

## 3. Admin Dashboard Framework: react-admin ✅

**GitHub:** https://github.com/marmelab/react-admin
**NPM:** `react-admin`
**Stars:** Very high popularity

### Features
- ✅ **Backend Agnostic** - Works with any REST/GraphQL API
- ✅ **45+ Data Provider Adapters** - Pre-built integrations
- ✅ **Authentication** - Built-in auth system
- ✅ **RBAC** - Role-based access control
- ✅ **Material-UI** - Professional design
- ✅ **TypeScript** - Full type safety
- ✅ **Optimistic Rendering** - Fast UX
- ✅ **i18n** - Internationalization
- ✅ **Theming** - Customizable

### Components
- `<Admin>` - Main app wrapper
- `<Resource>` - CRUD pages per entity
- `<List>`, `<Edit>`, `<Create>` - Standard views
- `<DataTable>` - Data grid
- `<SimpleForm>` - Form builder

### Data Provider Pattern
```javascript
const dataProvider = {
  getList: (resource, params) => Promise,
  getOne: (resource, params) => Promise,
  create: (resource, params) => Promise,
  update: (resource, params) => Promise,
  delete: (resource, params) => Promise,
};
```

**Note:** react-admin is a full framework, might be too opinionated for custom dashboard needs.

---

## 4. UI Component Libraries

### Material-UI (MUI) ✅
**URL:** https://mui.com/
**NPM:** `@mui/material`

- ✅ Most popular React UI library
- ✅ Professional design
- ✅ Comprehensive components
- ✅ Theming system
- ✅ Already used in project

### Ant Design ✅
**URL:** https://ant.design/
**NPM:** `antd`

- ✅ Enterprise-grade UI
- ✅ Rich component set
- ✅ Dashboard templates
- ✅ Already used in project

### Shadcn UI ✅
**URL:** https://ui.shadcn.com/
**NPM:** Not a package, copy-paste components

- ✅ Modern, minimalist
- ✅ Tailwind CSS based
- ✅ Radix UI primitives
- ✅ Full customization
- ✅ Already used in project (Radix components)

---

## 5. Design Patterns & Examples

### Dashboard Layout Pattern
```
┌─────────────────────────────────────────────┐
│  Header (Logo, User, Actions)              │
├──────────┬──────────────────────────────────┤
│          │                                  │
│  Sidebar │  Main Content (Grid Layout)     │
│  (Fixed) │  - Draggable Widgets            │
│          │  - Resizable Widgets            │
│          │  - Add/Remove Widgets           │
│          │                                  │
└──────────┴──────────────────────────────────┘
```

### Multi-Tenant Architecture
- User ID + Organization ID → Unique layout
- Backend API endpoints:
  - `GET /api/dashboard/layout?userId=X&orgId=Y`
  - `POST /api/dashboard/layout` (save layout)
  - `GET /api/widgets` (available widgets)
  - `GET /api/widgets/:id/data` (widget data)

### State Management
- Layout state: react-grid-layout
- Widget data: React Query / SWR
- User state: Context API / Zustand (already in project)

---

## 6. Recommended Stack

### Core Libraries
1. **react-grid-layout** - Grid system with drag & drop
2. **react-pro-sidebar** OR **Shadcn Sidebar** - Fixed sidebar
3. **@mui/material** OR **antd** - UI components (already in project)
4. **react-query** - Data fetching (already in project)
5. **zustand** - State management (already in project)

### Additional Tools
- **react-resizable** - Comes with react-grid-layout
- **lucide-react** - Icons (already in project)
- **framer-motion** - Animations (already in project)

---

## 7. Implementation Plan

### Phase 1: Sidebar
- Create fixed right sidebar component
- Add widget library/toolbox
- Implement collapse/expand
- Add navigation items

### Phase 2: Grid Layout
- Install react-grid-layout
- Create ResponsiveGridLayout wrapper
- Implement drag & drop
- Add resize handles
- Configure breakpoints

### Phase 3: Widgets
- Create base Widget component
- Implement widget registry
- Add widget data fetching
- Create widget types (chart, table, stats, etc.)

### Phase 4: Backend Integration
- Create API endpoints for layout CRUD
- Implement save/load layout per user+org
- Add widget data endpoints
- Implement RBAC for widgets

### Phase 5: Polish
- Add animations
- Implement loading states
- Add error handling
- Create widget settings modal
- Add export/import layout

---

## 8. Code Examples

### Example 1: Basic Grid Layout
```javascript
import GridLayout from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

function Dashboard() {
  const [layout, setLayout] = useState([
    { i: "a", x: 0, y: 0, w: 1, h: 2 },
    { i: "b", x: 1, y: 0, w: 3, h: 2 },
    { i: "c", x: 4, y: 0, w: 1, h: 2 }
  ]);

  return (
    <GridLayout
      className="layout"
      layout={layout}
      cols={12}
      rowHeight={30}
      width={1200}
      onLayoutChange={(newLayout) => setLayout(newLayout)}
    >
      <div key="a">Widget A</div>
      <div key="b">Widget B</div>
      <div key="c">Widget C</div>
    </GridLayout>
  );
}
```

### Example 2: Responsive Grid
```javascript
import { Responsive as ResponsiveGridLayout, WidthProvider } from "react-grid-layout";

const ResponsiveGrid = WidthProvider(ResponsiveGridLayout);

function Dashboard() {
  const layouts = {
    lg: [
      { i: "a", x: 0, y: 0, w: 4, h: 2 },
      { i: "b", x: 4, y: 0, w: 4, h: 2 },
      { i: "c", x: 8, y: 0, w: 4, h: 2 }
    ],
    md: [
      { i: "a", x: 0, y: 0, w: 5, h: 2 },
      { i: "b", x: 5, y: 0, w: 5, h: 2 },
      { i: "c", x: 0, y: 2, w: 10, h: 2 }
    ]
  };

  return (
    <ResponsiveGrid
      className="layout"
      layouts={layouts}
      breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
      cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
      rowHeight={30}
      onLayoutChange={(layout, allLayouts) => {
        console.log("Layout changed:", allLayouts);
      }}
    >
      <div key="a">Widget A</div>
      <div key="b">Widget B</div>
      <div key="c">Widget C</div>
    </ResponsiveGrid>
  );
}
```

### Example 3: Save to Backend
```javascript
function Dashboard() {
  const { userId, orgId } = useAuth();
  const [layout, setLayout] = useState([]);

  // Load layout from backend
  useEffect(() => {
    fetch(`/api/dashboard/layout?userId=${userId}&orgId=${orgId}`)
      .then(res => res.json())
      .then(data => setLayout(data.layout));
  }, [userId, orgId]);

  // Save layout to backend
  const handleLayoutChange = (newLayout) => {
    setLayout(newLayout);
    
    fetch('/api/dashboard/layout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        userId,
        orgId,
        layout: newLayout
      })
    });
  };

  return (
    <GridLayout
      layout={layout}
      onLayoutChange={handleLayoutChange}
      // ... other props
    >
      {/* widgets */}
    </GridLayout>
  );
}
```

---

## 9. References

- react-grid-layout: https://github.com/react-grid-layout/react-grid-layout
- react-grid-layout demos: https://react-grid-layout.github.io/react-grid-layout/
- react-pro-sidebar: https://github.com/azouaoui-med/react-pro-sidebar
- react-admin: https://github.com/marmelab/react-admin
- Shadcn UI Sidebar: https://ui.shadcn.com/docs/components/sidebar
- Material-UI: https://mui.com/
- Ant Design: https://ant.design/

---

## 10. Next Steps

1. ✅ Install react-grid-layout
2. ✅ Create sidebar component
3. ✅ Design widget system architecture
4. ✅ Implement basic grid layout
5. ✅ Add drag & drop functionality
6. ✅ Connect to backend API
7. ✅ Test with multi-tenant data
8. ✅ Deploy to staging

