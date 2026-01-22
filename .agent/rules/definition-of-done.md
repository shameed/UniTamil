---
name: definition-of-done
description: A mandatory quality checklist used to verify that tasks meet the workspace's high engineering standards.
---

# Definition of Done (DoD)

Before any feature, refactor, or fix is considered complete, the following criteria must be met and verified by the relevant expert skill:

## 1. Architectural Alignment (`pro-solution-architect`)
- [ ] The implementation matches the agreed-upon High-Level Design (HLD).
- [ ] Any deviations are documented in an updated ADR.

## 2. User Experience & Accessibility (`pro-ui-ux-engineer`)
- [ ] UI matches the design tokens (typography, spacing, colors).
- [ ] Components are keyboard-navigable and meet WCAG AA standards.
- [ ] States (loading, empty, error) are implemented and graceful.

## 3. Code Excellence (`pro-programmer`)
- [ ] Code is DRY, SOLID, and follows the workspace's naming conventions.
- [ ] Error handling is proactive and provides meaningful feedback.
- [ ] No "magic numbers" or hardcoded configurations.

## 4. Technical Integration (`pro-front-end-engineer` & `pro-back-end-engineer`)
- [ ] API contracts are fully implemented and validated.
- [ ] Performance meets the "Critical Path" thresholds (e.g., LCP < 2.5s).
- [ ] Security headers (CSP) and input sanitization are active.

## 5. Verification (`pro-front-end-testing-engineer`)
- [ ] Unit tests cover all core logic (>80% coverage).
- [ ] Critical paths are covered by deterministic E2E tests.
- [ ] Visual regression snapshots have been updated and verified.

## 6. AI & Logic (`pro-ai-engineer`)
- [ ] RAG/LLM responses are evaluated for grounding and accuracy.
- [ ] Model latency is within acceptable bounds.