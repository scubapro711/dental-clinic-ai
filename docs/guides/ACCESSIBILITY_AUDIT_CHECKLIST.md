# Accessibility Audit Checklist
## WCAG 2.1 AA Compliance

**Status:** In Progress  
**Target:** WCAG 2.1 AA  
**Current:** ~30% compliant  
**Date:** October 11, 2025  

---

## 🎯 WCAG 2.1 AA Requirements

### 1. Perceivable ⏳
Information and user interface components must be presentable to users in ways they can perceive.

#### 1.1 Text Alternatives
- [ ] All images have alt text
- [ ] Decorative images have empty alt=""
- [ ] Icons have aria-label
- [ ] Charts have text descriptions

#### 1.2 Time-based Media
- [ ] Videos have captions
- [ ] Audio has transcripts
- [ ] (N/A - no video/audio currently)

#### 1.3 Adaptable
- [ ] Content structure is semantic (headings, lists, etc.)
- [ ] Reading order is logical
- [ ] Form labels are associated with inputs
- [ ] Tables have proper headers

#### 1.4 Distinguishable
- [ ] Color contrast ratio ≥ 4.5:1 for normal text
- [ ] Color contrast ratio ≥ 3:1 for large text
- [ ] Text can be resized to 200%
- [ ] No information conveyed by color alone
- [ ] Audio control available

---

### 2. Operable ⏳
User interface components and navigation must be operable.

#### 2.1 Keyboard Accessible
- [ ] All functionality available via keyboard
- [ ] No keyboard traps
- [ ] Keyboard shortcuts don't conflict
- [ ] Focus visible at all times

#### 2.2 Enough Time
- [ ] No time limits (or adjustable)
- [ ] Can pause/stop moving content
- [ ] Can extend timeouts

#### 2.3 Seizures and Physical Reactions
- [ ] No flashing content >3 times/second
- [ ] No motion-triggered content

#### 2.4 Navigable
- [ ] Skip navigation link
- [ ] Page titles are descriptive
- [ ] Focus order is logical
- [ ] Link purpose is clear
- [ ] Multiple ways to find pages
- [ ] Headings and labels are descriptive
- [ ] Focus is visible

#### 2.5 Input Modalities
- [ ] Gestures have keyboard alternatives
- [ ] Touch targets ≥44x44 pixels
- [ ] No accidental activation

---

### 3. Understandable ⏳
Information and operation of user interface must be understandable.

#### 3.1 Readable
- [ ] Page language is identified
- [ ] Language changes are marked
- [ ] Unusual words are defined

#### 3.2 Predictable
- [ ] Focus doesn't cause unexpected changes
- [ ] Input doesn't cause unexpected changes
- [ ] Navigation is consistent
- [ ] Components are consistent

#### 3.3 Input Assistance
- [ ] Error messages are clear
- [ ] Labels and instructions provided
- [ ] Error suggestions provided
- [ ] Error prevention for important actions
- [ ] Help is available

---

### 4. Robust ⏳
Content must be robust enough to be interpreted by assistive technologies.

#### 4.1 Compatible
- [ ] Valid HTML (no duplicate IDs)
- [ ] ARIA roles used correctly
- [ ] Status messages announced
- [ ] Name, role, value for all components

---

## 🔍 Component-by-Component Audit

### SimpleMockLogin ⏳

**Status:** 40% compliant

**Issues:**
- ❌ Radio buttons need aria-label
- ❌ Button needs aria-describedby
- ❌ Form needs role="form"
- ❌ Warning message needs role="alert"
- ⚠️ Focus styles could be better

**Fixes Needed:**
```jsx
<input
  type="radio"
  aria-label="Select Clinic Portal"
  checked={selectedRole === 'clinic'}
/>

<button
  aria-describedby="portal-description"
  aria-label="Login to selected portal"
>
  Enter Portal
</button>

<div role="alert" className="...">
  ⚠️ Demo Mode
</div>
```

---

### AgenticDashboard ⏳

**Status:** 30% compliant

**Issues:**
- ❌ No skip navigation link
- ❌ Panel toggle buttons need aria-label
- ❌ Widgets need aria-label
- ❌ Chat input needs aria-label
- ❌ Agent activity needs aria-live
- ⚠️ Focus management needs work

**Fixes Needed:**
```jsx
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>

<Button
  aria-label="Toggle left widgets panel"
  aria-expanded={showLeftWidgets}
>
  <PanelLeftClose />
</Button>

<div
  role="region"
  aria-label="Agent activity"
  aria-live="polite"
>
  {activeAgent && ...}
</div>
```

---

### PatientLayout ⏳

**Status:** 50% compliant

**Issues:**
- ❌ Mobile menu button needs aria-label
- ❌ Mobile menu needs aria-expanded
- ❌ Navigation needs aria-label
- ❌ Logout button needs confirmation
- ⚠️ Focus trap in mobile menu

**Fixes Needed:**
```jsx
<button
  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
  aria-label="Toggle navigation menu"
  aria-expanded={mobileMenuOpen}
  aria-controls="mobile-menu"
>
  <Menu />
</button>

<nav
  id="mobile-menu"
  aria-label="Main navigation"
  className={mobileMenuOpen ? 'block' : 'hidden'}
>
  ...
</nav>
```

---

### ClinicLayout ⏳

**Status:** 50% compliant

**Issues:**
- ❌ Same as PatientLayout
- ❌ Role badge needs aria-label
- ❌ Navigation icons need aria-hidden

**Fixes Needed:**
```jsx
<span
  className="..."
  aria-label={`User role: ${formatRoleName(user.role)}`}
>
  {formatRoleName(user.role)}
</span>

<Link to="/clinic/dashboard">
  <span aria-hidden="true">🎯</span>
  Dashboard
</Link>
```

---

## 🎨 Color Contrast Audit

### Current Issues

1. **Blue on Blue** ⚠️
   - Clinic header: Blue-200 text on Blue-600 background
   - Contrast ratio: ~2.8:1 (needs 4.5:1)
   - **Fix:** Use white text instead

2. **Gray on Gray** ⚠️
   - Disabled buttons: Gray-400 on Gray-200
   - Contrast ratio: ~2.1:1 (needs 3:1)
   - **Fix:** Use Gray-600 on Gray-200

3. **Link Colors** ⚠️
   - Blue-600 on white: 4.5:1 ✅
   - Blue-500 on gray-50: 3.8:1 ❌
   - **Fix:** Use Blue-700 on light backgrounds

### Tools to Use
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- Chrome DevTools Accessibility Panel
- axe DevTools extension

---

## ⌨️ Keyboard Navigation Audit

### Required Keyboard Shortcuts

| Action | Shortcut | Status |
|--------|----------|--------|
| Navigate forward | Tab | ✅ Works |
| Navigate backward | Shift+Tab | ✅ Works |
| Activate button | Enter/Space | ✅ Works |
| Close modal | Escape | ⏳ Not tested |
| Open menu | Enter | ⏳ Not tested |
| Navigate menu | Arrow keys | ❌ Not implemented |
| Submit form | Enter | ✅ Works |

### Focus Management

**Issues:**
- ❌ Focus not visible on all elements
- ❌ Focus trap missing in modals
- ❌ Focus not restored after modal close
- ❌ Skip navigation link missing

**Fixes Needed:**
```css
/* Add visible focus styles */
*:focus {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}

/* Skip navigation link */
.sr-only:focus {
  position: absolute;
  left: 0;
  top: 0;
  z-index: 9999;
  padding: 1rem;
  background: white;
  color: black;
}
```

---

## 🔊 Screen Reader Testing

### Tools
- NVDA (Windows) - Free
- JAWS (Windows) - Commercial
- VoiceOver (Mac) - Built-in
- TalkBack (Android) - Built-in

### Test Scenarios
- [ ] Login flow
- [ ] Navigate dashboard
- [ ] Use chat interface
- [ ] Fill forms
- [ ] Read notifications
- [ ] Navigate menus
- [ ] Use widgets

### Common Issues
- ❌ Images without alt text
- ❌ Buttons without labels
- ❌ Form inputs without labels
- ❌ Dynamic content not announced
- ❌ Loading states not announced

---

## 📋 Quick Wins (1-2 hours)

### 1. Add ARIA Labels (30 min)
```jsx
// Buttons
<button aria-label="Close dialog">×</button>
<button aria-label="Search">🔍</button>

// Icons
<span aria-hidden="true">🦷</span>

// Inputs
<input aria-label="Search patients" />

// Regions
<div role="region" aria-label="Chat messages">
```

### 2. Fix Color Contrast (30 min)
```css
/* Before: Blue-200 on Blue-600 (2.8:1) */
.text-blue-200 { color: #BFDBFE; }

/* After: White on Blue-600 (4.5:1+) */
.text-white { color: #FFFFFF; }
```

### 3. Add Focus Styles (15 min)
```css
*:focus {
  outline: 2px solid #3B82F6;
  outline-offset: 2px;
}

*:focus:not(:focus-visible) {
  outline: none;
}
```

### 4. Add Skip Navigation (15 min)
```jsx
<a href="#main-content" className="sr-only focus:not-sr-only">
  Skip to main content
</a>

<main id="main-content">
  ...
</main>
```

---

## 🎯 Priority Levels

### P0 - Critical (Must Fix)
- [ ] Color contrast issues
- [ ] Missing alt text
- [ ] Keyboard traps
- [ ] Missing form labels

### P1 - High (Should Fix)
- [ ] ARIA labels for buttons
- [ ] Focus management
- [ ] Skip navigation
- [ ] Screen reader announcements

### P2 - Medium (Nice to Have)
- [ ] Keyboard shortcuts
- [ ] Better focus styles
- [ ] ARIA live regions
- [ ] Error prevention

### P3 - Low (Future)
- [ ] Gesture alternatives
- [ ] Motion preferences
- [ ] High contrast mode
- [ ] Dyslexia-friendly fonts

---

## 📊 Progress Tracking

| Category | Current | Target | Status |
|----------|---------|--------|--------|
| Text Alternatives | 20% | 100% | ⏳ |
| Keyboard Access | 60% | 100% | ⏳ |
| Color Contrast | 70% | 100% | ⏳ |
| ARIA Labels | 10% | 100% | ⏳ |
| Focus Management | 40% | 100% | ⏳ |
| Screen Reader | 20% | 90% | ⏳ |
| **Overall** | **30%** | **100%** | ⏳ |

---

## 🚀 Implementation Plan

### Phase 1: Quick Wins (1-2 hours)
1. Add ARIA labels to all buttons
2. Fix color contrast issues
3. Add focus styles
4. Add skip navigation

### Phase 2: Forms & Inputs (1-2 hours)
1. Add labels to all inputs
2. Add error messages
3. Add field descriptions
4. Add validation feedback

### Phase 3: Dynamic Content (1-2 hours)
1. Add aria-live regions
2. Announce loading states
3. Announce errors
4. Announce successes

### Phase 4: Testing (1-2 hours)
1. Test with keyboard only
2. Test with screen reader
3. Test color contrast
4. Fix issues found

---

**Total Estimated Time:** 4-8 hours  
**Priority:** High (Required for production)  
**Compliance Target:** WCAG 2.1 AA  

---

*This checklist will be updated as accessibility improvements are implemented.*
