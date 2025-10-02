# Architecture Decision Records (ADR)

This directory contains Architecture Decision Records (ADRs) for the Dental Clinic AI project.

## What is an ADR?

An ADR is a document that captures an important architectural decision made along with its context and consequences.

## Why ADRs?

ADRs help us:
- **Document decisions:** Remember why we made certain choices
- **Prevent drift:** Avoid undocumented changes that cause confusion
- **Onboard new team members:** Understand the project's evolution
- **Review decisions:** Evaluate if past decisions still make sense

## ADR Index

| ADR | Title | Date | Status |
|-----|-------|------|--------|
| [ADR-001](./ADR-001-merge-four-agents-into-alex.md) | Merge Four Specialized Agents into Unified Alex Agent | 2025-10-02 | ✅ Accepted |
| [ADR-002](./ADR-002-openmanus-to-langgraph-migration.md) | Migrate from OpenManus to LangGraph | 2025-10-02 | ✅ Accepted |
| [ADR-003](./ADR-003-defer-portfolio-a-to-post-mvp.md) | Defer Portfolio A Agents to Post-MVP | 2025-10-02 | ✅ Accepted |
| [ADR-004](./ADR-004-hybrid-architecture-three-agents.md) | Hybrid Architecture with Three Core Agents | 2025-10-02 | ✅ Accepted |

## ADR Lifecycle

### Statuses

- **Proposed:** Decision is being considered
- **Accepted:** Decision has been made and implemented
- **Deprecated:** Decision is no longer relevant
- **Superseded:** Decision has been replaced by a newer ADR

### When to Create an ADR

Create an ADR when making decisions about:
- **Architecture:** Agent structure, frameworks, databases
- **Technology:** Choosing libraries, services, platforms
- **Process:** Development workflow, testing strategy
- **Scope:** What to build, what to defer, what to remove

### When NOT to Create an ADR

Don't create an ADR for:
- **Implementation details:** Variable names, code style
- **Temporary decisions:** Quick experiments, prototypes
- **Obvious choices:** Using Python for a Python project

## How to Create an ADR

1. **Copy the template:**
   ```bash
   cp docs/adr/TEMPLATE.md docs/adr/ADR-XXX-your-title.md
   ```

2. **Fill in the sections:**
   - Context: What's the situation?
   - Decision: What did we decide?
   - Consequences: What are the effects?
   - Alternatives: What else did we consider?

3. **Get approval:**
   - Review with team
   - Update status to "Accepted"

4. **Commit with ADR reference:**
   ```bash
   git commit -m "feat: implement feature X

   See ADR-XXX for rationale.

   Manus-Session-ID: [session-id]"
   ```

## Git Hook

A git hook enforces ADR creation for certain changes:

**Triggers:**
- Deleting agent files
- Removing major features
- Changing core architecture

**Action:**
- Blocks commit if no ADR exists
- Prompts to create ADR

**Install:**
```bash
cp scripts/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## References

- **ADR Template:** [TEMPLATE.md](./TEMPLATE.md)
- **Framework:** [IMPROVED_FRAMEWORK_V2.0.md](../../IMPROVED_FRAMEWORK_V2.md)
- **Work Plan:** [WORK_PLAN_V19.0_UNIFIED.md](../../WORK_PLAN_V19.0_UNIFIED.md)

---

**Last Updated:** 2025-10-02  
**Maintainer:** scubapro711
