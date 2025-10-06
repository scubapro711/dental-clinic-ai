# 🦷 Odontogram Component - Design Specification

**Date:** October 6, 2025  
**Module:** 1.5 - PIM Core  
**Task:** 1.5.1 - Odontogram Component  
**Priority:** 🔴 Critical for Pilot

---

## 📋 Overview

The Odontogram is an interactive dental chart that displays all 32 adult teeth, allowing dentists to:
- View tooth status and conditions
- Mark treatments performed
- Track treatment history
- Plan future treatments
- Document findings visually

---

## 🦷 Dental Anatomy

### Adult Dentition (32 teeth)

**Quadrants (FDI Notation):**
- **Quadrant 1:** Upper Right (11-18)
- **Quadrant 2:** Upper Left (21-28)
- **Quadrant 3:** Lower Left (31-38)
- **Quadrant 4:** Lower Right (41-48)

**Tooth Types per Quadrant:**
1. Central Incisor
2. Lateral Incisor
3. Canine
4. First Premolar
5. Second Premolar
6. First Molar
7. Second Molar
8. Third Molar (Wisdom tooth)

---

## 🎨 UI Design

### Layout

```
        Upper Jaw
    18 17 16 15 14 13 12 11 | 21 22 23 24 25 26 27 28
    ------------------------------------------------
    |                                                |
    |              Patient View                      |
    |                                                |
    ------------------------------------------------
    48 47 46 45 44 43 42 41 | 31 32 33 34 35 36 37 38
        Lower Jaw
```

### Visual Elements

**Each Tooth:**
- SVG representation of tooth shape
- Tooth number (FDI notation)
- Status indicator (color-coded)
- Treatment markers
- Clickable/selectable
- Hover tooltip with details

**Color Coding:**
- 🟢 **Green:** Healthy
- 🟡 **Yellow:** Watch/Monitor
- 🟠 **Orange:** Treatment needed
- 🔴 **Red:** Urgent/Pain
- ⚫ **Gray:** Missing
- 🔵 **Blue:** Treated/Restored

---

## 📊 Data Structure

### Tooth Model

```typescript
interface Tooth {
  id: number;                    // FDI notation (11-48)
  quadrant: 1 | 2 | 3 | 4;       // Quadrant number
  position: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8;  // Position in quadrant
  type: 'incisor' | 'canine' | 'premolar' | 'molar';
  status: ToothStatus;
  conditions: ToothCondition[];
  treatments: Treatment[];
  notes: string;
}

interface ToothStatus {
  code: 'healthy' | 'watch' | 'needs_treatment' | 'urgent' | 'missing' | 'treated';
  label: string;
  color: string;
  updatedAt: string;
  updatedBy: string;
}

interface ToothCondition {
  id: string;
  type: 'cavity' | 'fracture' | 'wear' | 'sensitivity' | 'other';
  severity: 'mild' | 'moderate' | 'severe';
  surface?: 'occlusal' | 'mesial' | 'distal' | 'buccal' | 'lingual';
  description: string;
  diagnosedAt: string;
  diagnosedBy: string;
}

interface Treatment {
  id: string;
  type: 'filling' | 'crown' | 'root_canal' | 'extraction' | 'cleaning' | 'other';
  status: 'planned' | 'in_progress' | 'completed' | 'cancelled';
  date: string;
  dentist: string;
  cost: number;
  notes: string;
  materials?: string[];
}
```

### Odontogram Model

```typescript
interface Odontogram {
  id: string;
  patientId: string;
  teeth: Tooth[];              // Array of 32 teeth
  createdAt: string;
  updatedAt: string;
  lastExamDate?: string;
  nextExamDate?: string;
}
```

---

## 🎯 Features

### Phase 1: Basic Display (Day 1-2)
- ✅ Display 32 teeth in correct layout
- ✅ FDI notation labels
- ✅ Quadrant separation
- ✅ Responsive design
- ✅ Basic tooth shapes (SVG)

### Phase 2: Interactive Selection (Day 3-5)
- ✅ Click to select tooth
- ✅ Multi-select (Ctrl+Click)
- ✅ Hover tooltips
- ✅ Status color coding
- ✅ Selected state visual feedback

### Phase 3: Treatment History (Day 6-7)
- ✅ View tooth details panel
- ✅ Treatment history list
- ✅ Condition markers
- ✅ Add new treatment
- ✅ Edit existing treatment

### Phase 4: Backend Integration (Day 8-9)
- ✅ API endpoints for CRUD
- ✅ Save/load odontogram
- ✅ Update tooth status
- ✅ Add/edit treatments
- ✅ History tracking

### Phase 5: Advanced Features (Day 10)
- ✅ Export to PDF
- ✅ Print view
- ✅ Compare with previous exams
- ✅ Treatment planning mode

---

## 🔧 Technical Implementation

### Frontend Components

```
src/components/odontogram/
├── Odontogram.jsx              # Main container
├── ToothChart.jsx              # 32-tooth layout
├── Tooth.jsx                   # Single tooth component
├── ToothDetails.jsx            # Details panel
├── TreatmentHistory.jsx        # Treatment list
├── AddTreatmentModal.jsx       # Add treatment form
└── odontogram.css              # Styles
```

### Backend API

```python
# backend/app/api/v1/endpoints/odontogram.py

@router.get("/patients/{patient_id}/odontogram")
async def get_odontogram(patient_id: int)
    """Get patient's odontogram"""

@router.post("/patients/{patient_id}/odontogram")
async def create_odontogram(patient_id: int, data: OdontogramCreate)
    """Create new odontogram"""

@router.put("/patients/{patient_id}/odontogram/{odontogram_id}")
async def update_odontogram(...)
    """Update odontogram"""

@router.put("/patients/{patient_id}/odontogram/{odontogram_id}/teeth/{tooth_id}")
async def update_tooth(...)
    """Update single tooth"""

@router.post("/patients/{patient_id}/odontogram/{odontogram_id}/teeth/{tooth_id}/treatments")
async def add_treatment(...)
    """Add treatment to tooth"""
```

---

## 🎨 UI/UX Guidelines

### Visual Design
- Clean, professional medical interface
- High contrast for visibility
- Touch-friendly (mobile support)
- Accessible (keyboard navigation)
- RTL support for Hebrew

### Interactions
- **Click:** Select tooth
- **Ctrl+Click:** Multi-select
- **Right-click:** Context menu
- **Hover:** Show tooltip
- **Double-click:** Open details

### Responsiveness
- Desktop: Full chart + side panel
- Tablet: Stacked layout
- Mobile: Scrollable chart

---

## 📱 User Flows

### 1. View Patient's Odontogram
```
Doctor opens patient file
→ Navigate to Odontogram tab
→ System loads latest odontogram
→ Display 32 teeth with current status
→ Doctor can view details by clicking teeth
```

### 2. Mark New Condition
```
Doctor clicks tooth #16
→ Details panel opens
→ Click "Add Condition"
→ Select condition type (e.g., cavity)
→ Select severity and surface
→ Add notes
→ Save
→ Tooth color updates
```

### 3. Add Treatment
```
Doctor selects tooth #24
→ Click "Add Treatment"
→ Select treatment type (e.g., filling)
→ Set status (planned/completed)
→ Add date, cost, materials
→ Save
→ Treatment appears in history
```

### 4. Plan Multiple Treatments
```
Doctor Ctrl+clicks teeth #11, #12, #13
→ Click "Plan Treatment"
→ Select treatment type
→ Set dates and costs
→ Generate treatment plan
→ Save for patient approval
```

---

## 🧪 Testing Requirements

### Unit Tests
- Tooth component rendering
- Status color mapping
- FDI notation conversion
- Data validation

### Integration Tests
- Load odontogram from API
- Save changes to backend
- Update tooth status
- Add/edit treatments

### E2E Tests
- Complete examination workflow
- Treatment planning workflow
- Export/print functionality

---

## 📊 Success Metrics

- ✅ All 32 teeth display correctly
- ✅ Click response < 100ms
- ✅ API response < 500ms
- ✅ Mobile-friendly (touch targets ≥ 44px)
- ✅ Accessible (WCAG 2.1 AA)
- ✅ Works offline (with cache)

---

## 🚀 Implementation Plan

### Day 1-2: Design & Basic Display
- Create component structure
- Implement tooth layout
- Add FDI notation
- Basic styling

### Day 3-5: Interactive Features
- Click handlers
- Selection state
- Tooltips
- Status colors

### Day 6-7: Treatment History
- Details panel
- Treatment list
- Add/edit forms
- History display

### Day 8-9: Backend Integration
- API endpoints
- Data persistence
- Load/save functionality
- Error handling

### Day 10: Polish & Testing
- Export/print
- Performance optimization
- Bug fixes
- Documentation

---

## 📚 References

- **FDI Notation:** https://en.wikipedia.org/wiki/FDI_World_Dental_Federation_notation
- **Dental Anatomy:** Standard dental textbooks
- **UI Patterns:** Modern dental software (Dentrix, Open Dental)
- **Accessibility:** WCAG 2.1 guidelines

---

## ✅ Deliverables

1. ✅ Odontogram React component
2. ✅ Backend API endpoints
3. ✅ Data models and schemas
4. ✅ Unit and integration tests
5. ✅ User documentation
6. ✅ Technical documentation

---

**Next Steps:**
1. Review and approve design
2. Start implementation (Phase 1)
3. Iterate based on feedback

---

**Created:** 2025-10-06  
**Status:** Design Complete  
**Ready for:** Implementation
