# Contributing to DentaFlow

**Status:** ✅ Current | **Last Updated:** November 21, 2025

This document provides guidelines for making contributions to DentaFlow. It is optimized for AI development agents and combines best practices from previous versions.

---

## 1. Core Principles for Contribution

- **Follow the Plan:** All work should align with the active development plan. Propose changes to the plan before deviating.
- **Context is Key:** Before starting a task, refresh your context by reviewing the main `README.md` and `ARCHITECTURE.md`.
- **Write Quality Code:** Adhere to the style guides and write clean, readable, and maintainable code.
- **Test Everything:** If it's not tested, it's considered broken. Every feature requires tests.

---

## 2. How to Contribute

### Reporting Bugs & Suggesting Enhancements

- Use the **Issue Templates** on GitHub (Bug Report, Feature Request).
- Provide clear, descriptive titles and detailed descriptions.

### Making Code Contributions

1. **Create a Branch:** Create a feature or bugfix branch from the `develop` branch.
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feat/your-descriptive-feature-name
   ```

2. **Make Changes:** Implement your feature or fix.

3. **Run Tests:** Ensure all existing and new tests pass.
   ```bash
   # Backend tests
   cd backend && pytest

   # Frontend tests
   cd ../frontend && pnpm test
   ```

4. **Commit Changes:** Use the Conventional Commits format.
   ```bash
   git commit -m "feat(api): add new endpoint for patient search"
   ```

5. **Create a Pull Request (PR):** Push your branch and open a PR against the `develop` branch.

---

## 3. Git Workflow & Style Guides

### Git Branching

- **`main`:** Production-ready code.
- **`develop`:** Staging and integration branch.
- **`feat/...`:** New features (from `develop`).
- **`fix/...`:** Bug fixes (from `develop`).

### Commit Messages (Conventional Commits)

**Format:** `type(scope): subject`

- **`feat`:** A new feature.
- **`fix`:** A bug fix.
- **`docs`:** Documentation only changes.
- **`refactor`:** Code refactoring.
- **`test`:** Adding or improving tests.
- **`chore`:** Build process or tooling changes.

### Code Style

- **Python (Backend):** PEP 8, `black` for formatting, `ruff` for linting.
- **TypeScript (Frontend):** Airbnb style guide, `prettier` for formatting, ESLint for linting.
- **Pre-commit Hooks:** Are installed to automatically enforce style and prevent committing secrets.

---

## 4. Pull Request (PR) Process

### PR Checklist

- [ ] All tests pass locally (Backend & Frontend).
- [ ] Code coverage meets requirements (80%+).
- [ ] Pre-commit hooks pass.
- [ ] Documentation is updated to reflect changes.
- [ ] PR has a clear description and is linked to an issue.

### Review Process

- **Automated Checks:** All CI checks in GitHub Actions must pass.
- **Code Review:** At least one approval from a team member is required.
- **Merge:** Use "Squash and merge" for feature branches.

---

## 5. Repository Hygiene

- **DO NOT COMMIT:** Secrets, large files (>500KB), generated files (`node_modules`, `__pycache__`), or OS/IDE files (`.DS_Store`, `.idea`).
- **Keep it Clean:** Use the `.gitignore` file, delete merged branches, and keep the commit history clean.

---

## 6. Related Documents

- **[README.md](../README.md):** Main project overview.
- **[DEVELOPMENT.md](docs/DEVELOPMENT.md):** Local setup and development guide.
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md):** System architecture overview.
