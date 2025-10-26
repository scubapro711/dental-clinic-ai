# DentaFlow Design System

Professional Agentic UX/UI design system for multi-agent dental clinic management.

## Overview

This design system implements research-backed principles for Agentic Systems UX, specifically tailored for healthcare applications. It provides a cohesive visual language that makes AI agent operations transparent, understandable, and trustworthy.

## Design Principles

1. **Transparency First** - Always show what agents are doing
2. **Human Control** - Users can intervene at any time
3. **Risk Awareness** - Clear indication of action consequences
4. **Trust Building** - Consistent, reliable agent behavior
5. **Healthcare Standards** - Medical-grade professionalism
6. **Multi-Agent Harmony** - Seamless coordination between agents
7. **Accessibility** - Inclusive design for all users
8. **Performance** - Fast, responsive, efficient

## File Structure

```
src/styles/
├── dashboard.css         # Dashboard layout, agent cards, status bar
├── transparency.css      # Activity panels, tool execution, reasoning
├── widgets.css          # Decision queue, revenue, patients, compliance
├── coordination.css     # Handoffs, parallel execution, conflicts
├── global.css          # Typography, buttons, forms, utilities
├── design-system.css   # Core variables and design tokens
├── accessibility.css   # WCAG 2.1 AA compliance
├── responsive.css      # Responsive breakpoints
└── README.md          # This file
```

## Agent Color Palette

Each agent has a unique visual identity:

| Agent | Role | Primary | Gradient |
|-------|------|---------|----------|
| **Alex** | Patient Experience | Indigo (#4F46E5) | Indigo → Light Indigo |
| **Sarah** | Clinical Support | Emerald (#10B981) | Emerald → Light Emerald |
| **Marcus** | Financial Intelligence | Amber (#F59E0B) | Amber → Light Amber |
| **Sophia** | Practice Operations | Violet (#8B5CF6) | Violet → Light Violet |
| **Harper** | HIPAA Compliance | Red (#EF4444) | Red → Light Red |

## CSS Variables

### Agent Colors
```css
--agent-alex-primary: #4F46E5;
--agent-alex-accent: #818CF8;
--agent-alex-gradient: linear-gradient(135deg, #4F46E5, #818CF8);
--agent-alex-light: #EEF2FF;
```

### Status Colors
```css
--status-active: #10B981;   /* Green */
--status-busy: #F59E0B;     /* Amber */
--status-error: #EF4444;    /* Red */
--status-idle: #9CA3AF;     /* Gray */
```

### Risk Levels
```css
--risk-low: #10B981;        /* Green */
--risk-medium: #F59E0B;     /* Amber */
--risk-high: #EF4444;       /* Red */
--risk-critical: #DC2626;   /* Dark Red */
```

### Spacing Scale
```css
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-12: 3rem;    /* 48px */
```

## Component Classes

### Agent Cards
```html
<div class="agent-card agent-card-alex">
  <div class="agent-card-header">
    <div class="agent-avatar agent-avatar-alex">👨‍⚕️</div>
    <div class="agent-card-info">
      <h3 class="agent-card-name">Alex</h3>
      <p class="agent-card-role">Patient Experience Agent</p>
    </div>
    <div class="agent-status-indicator agent-status-active"></div>
  </div>
</div>
```

### Decision Queue
```html
<div class="decision-item priority-high">
  <div class="decision-item-header">
    <div class="decision-priority-badge high">🔴 High Priority</div>
    <span class="decision-timestamp">2 hours ago</span>
  </div>
  <div class="decision-item-content">
    <h4 class="decision-item-title">Urgent Decision Required</h4>
    <p class="decision-item-description">Description...</p>
  </div>
  <div class="decision-item-actions">
    <button class="decision-action-btn approve">Approve</button>
    <button class="decision-action-btn chat">Chat</button>
    <button class="decision-action-btn reject">Reject</button>
  </div>
</div>
```

### Activity Feed
```html
<div class="activity-feed">
  <div class="activity-feed-header">
    <h3 class="activity-feed-title">
      <span class="activity-feed-live-indicator"></span>
      Live Activity
    </h3>
  </div>
  <div class="activity-feed-content">
    <div class="activity-feed-item">
      <div class="activity-feed-item-icon agent-avatar-alex">👨‍⚕️</div>
      <div class="activity-feed-item-content">
        <p class="activity-feed-item-text">Alex is scheduling appointment...</p>
        <p class="activity-feed-item-time">2 seconds ago</p>
      </div>
      <div class="activity-feed-item-status active">⚡</div>
    </div>
  </div>
</div>
```

### Healthcare Components
```html
<!-- Risk Indicator -->
<span class="risk-indicator risk-high">High Risk</span>

<!-- HIPAA Badge -->
<span class="hipaa-badge">🔒 HIPAA Compliant</span>

<!-- Privacy Indicator -->
<div class="privacy-indicator">
  🔒 Protected Health Information (PHI)
</div>

<!-- Clinical Evidence -->
<span class="evidence-badge">📊 Evidence-Based</span>
```

## Utility Classes

### Spacing
```css
.mt-4  /* margin-top: 1rem */
.mb-2  /* margin-bottom: 0.5rem */
.p-3   /* padding: 0.75rem */
```

### Flex Utilities
```css
.flex              /* display: flex */
.items-center      /* align-items: center */
.justify-between   /* justify-content: space-between */
.gap-2            /* gap: 0.5rem */
```

### Text Utilities
```css
.text-primary     /* color: var(--agent-alex-primary) */
.text-success     /* color: var(--status-active) */
.text-danger      /* color: var(--status-error) */
.font-bold        /* font-weight: 700 */
```

## Animations

### Keyframe Animations
```css
@keyframes pulse              /* Status indicators */
@keyframes pulse-glow         /* Agent card borders */
@keyframes slide-in-left      /* Activity feed items */
@keyframes slide-in-right     /* Decision queue items */
@keyframes agent-activate     /* Agent card activation */
@keyframes tool-execute       /* Tool execution */
@keyframes agent-handoff      /* Agent transitions */
@keyframes shimmer           /* Progress bars */
```

### Usage
```css
.agent-status-active {
  animation: pulse 2s ease-in-out infinite;
}

.agent-card {
  animation: agent-activate 0.5s var(--ease-smooth);
}
```

## Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 767px) { }

/* Tablet */
@media (min-width: 768px) and (max-width: 1919px) { }

/* Desktop */
@media (min-width: 1920px) { }
```

## Accessibility

### WCAG 2.1 Level AA Compliance

- ✅ Color contrast ratios ≥ 4.5:1
- ✅ Keyboard navigation support
- ✅ Screen reader compatibility
- ✅ Focus indicators
- ✅ ARIA labels and live regions
- ✅ High contrast mode support
- ✅ Reduced motion support

### Focus Indicators
```css
*:focus {
  outline: 2px solid var(--agent-alex-primary);
  outline-offset: 2px;
}
```

### Screen Reader Only
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

## Browser Support

- ✅ Chrome/Edge (Chromium) - Latest
- ✅ Firefox - Latest
- ✅ Safari - Latest
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

### CSS Bundle Size
- dashboard.css: 21KB
- transparency.css: 14KB
- widgets.css: 15KB
- coordination.css: 15KB
- global.css: 16KB
- **Total New CSS:** ~81KB (unminified)

### Optimization
- Use CSS minification in production
- Consider PurgeCSS for unused styles
- Enable CSS splitting by route
- Extract critical CSS for above-the-fold content

## Usage

### Import Order
```javascript
// In main.jsx
import './index.css'
import './styles/responsive.css'
import './styles/accessibility.css'
import './styles/global.css'

// In AgenticDashboard.jsx
import './Dashboard.css'
import '../styles/dashboard.css'
import '../styles/transparency.css'
import '../styles/widgets.css'
import '../styles/coordination.css'
```

### Component Development
1. Use semantic HTML
2. Apply utility classes for spacing/layout
3. Use component classes for specific UI elements
4. Follow agent color palette
5. Ensure accessibility compliance
6. Test responsive behavior

## Contributing

When adding new styles:

1. **Follow naming conventions**
   - Use kebab-case for class names
   - Prefix agent-specific classes with `agent-`
   - Use semantic names (e.g., `decision-item` not `red-box`)

2. **Document new components**
   - Add comments explaining purpose
   - Include usage examples
   - Document any dependencies

3. **Test accessibility**
   - Check color contrast
   - Verify keyboard navigation
   - Test with screen readers

4. **Optimize performance**
   - Avoid deep nesting
   - Use CSS variables
   - Minimize specificity

## Resources

- [DentaFlow Agentic UX Strategy](../../../dentaflow-agentic-ux-strategy.md)
- [Research Findings](../../../agentic-ux-research-findings.md)
- [Implementation Summary](../../../DENTAFLOW_AGENTIC_UX_REDESIGN_SUMMARY.md)

## License

Proprietary - DentaFlow System

---

**Version:** 1.0  
**Last Updated:** October 26, 2025  
**Maintainer:** DentaFlow Development Team
