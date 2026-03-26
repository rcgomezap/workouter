# Enhancement Documentation

This directory contains the comprehensive implementation plan for transforming the Workout Tracker API into a robust personal training platform.

## Quick Start

1. **Read the master plan**: Start with [`00-index.md`](./00-index.md)
2. **Begin with Phase 1**: Review [`phase1-summary.md`](./phase1-summary.md)
3. **Implement sequentially**: Follow tasks 01-04 in order
4. **Use subagents**: Each task includes subagent assignment templates

## Documentation Structure

```
docs/enhancement/
├── 00-index.md                          # Master enhancement plan (7 phases, 7 weeks)
├── README.md                            # This file
│
├── phase1-summary.md                    # Phase 1 overview (5-7 days)
├── 01-fix-session-filtering.md          # Task 1: Session filter implementation
├── 02-fix-bodyweight-filtering.md       # Task 2: Bodyweight date filtering
├── 03-fix-exercise-history-bug.md       # Task 3: Fix empty exercises arrays
└── 04-phase1-integration-testing.md     # Task 4: Comprehensive validation
```

## Implementation Timeline

| Phase | Duration | Tasks | Focus Area |
|-------|----------|-------|------------|
| **Phase 1** | 5-7 days | 01-04 | Foundation Fixes & Filtering |
| **Phase 2** | 10-12 days | 05-08 | Enhanced Analytics Core |
| **Phase 3** | 10-12 days | 09-13 | Advanced Insights & Benchmarking |
| **Phase 4** | 8-10 days | 14-18 | Search, Discovery & Session Lifecycle |
| **Phase 5** | 8-10 days | 19-23 | Bodyweight & Composition Analytics |
| **Phase 6** | 8-10 days | 24-28 | Feedback & Final Polish |

**Total**: 7 weeks (49 days) for complete transformation

## Phase 1 Tasks (Current Focus)

### ✅ Task 01: Fix Session Filtering (1-2 days)
**File**: [`01-fix-session-filtering.md`](./01-fix-session-filtering.md)

Fix session filtering that's currently defined but not implemented:
- status filter (PLANNED, IN_PROGRESS, COMPLETED)
- mesocycle_id filter
- date_from / date_to filters
- Proper pagination with filters

**Why Critical**: Enables users to find specific workouts efficiently.

---

### ✅ Task 02: Fix Bodyweight Filtering (0.5-1 day)
**File**: [`02-fix-bodyweight-filtering.md`](./02-fix-bodyweight-filtering.md)

Fix bodyweight date filtering (repository already works, just wire it up):
- date_from / date_to filters
- datetime → date conversion in resolver
- Repository methods already implemented

**Why Critical**: Required for bodyweight trend analysis.

---

### ✅ Task 03: Fix Exercise History Bug (1-2 days)
**File**: [`03-fix-exercise-history-bug.md`](./03-fix-exercise-history-bug.md)

Fix bug where exerciseHistory returns sessions with empty exercises arrays:
- Repository relationship loading issue
- Need proper `selectinload()` configuration
- May require subquery for exercise_id filtering

**Why Critical**: Makes exercise history query actually usable.

---

### ✅ Task 04: Phase 1 Integration Testing (0.5-1 day)
**File**: [`04-phase1-integration-testing.md`](./04-phase1-integration-testing.md)

Comprehensive validation before Phase 2:
- All 3 fixes work in isolation
- All 3 fixes work together
- No regressions introduced
- ≥85% test coverage
- Performance benchmarks

**Why Critical**: Quality gate before building on this foundation.

---

## How to Use These Documents

### For Each Task:

1. **Read the user story** - Understand the business value
2. **Review acceptance criteria** - Know what "done" looks like
3. **Follow implementation plan** - Step-by-step guide with code examples
4. **Run tests** - Unit, integration, and API tests
5. **Check success criteria** - Verify all boxes are checked
6. **Assign to subagent** - Use provided subagent template

### Task Document Structure

Every task document includes:
- 📖 **User Story** - Business context
- 📋 **Background** - Current state and issues
- ✅ **Acceptance Criteria** - Functional, technical, testing requirements
- 🔧 **Implementation Plan** - Step-by-step with code examples
- 🧪 **Testing Strategy** - Unit, integration, API tests
- 📁 **Files to Modify** - Specific file locations
- ☑️ **Success Checklist** - Mark tasks complete
- 💻 **Commands** - Copy-paste terminal commands
- 🤖 **Subagent Template** - Ready-to-use subagent instructions
- ➡️ **Next Steps** - What to do after completion

## Key Principles

### 1. Sequential Implementation
- Complete Phase 1 before Phase 2
- Complete each task before starting the next
- Don't skip integration testing

### 2. Test-Driven Development
- Write tests for every feature
- Maintain ≥85% coverage
- No regressions allowed

### 3. Subagent Usage
- Use `general` subagent for implementation
- Use `explore` subagent for debugging/analysis
- Follow subagent templates in each task

### 4. Code Quality
- 100% type hint coverage
- No linting errors (`ruff check`)
- Proper formatting (`ruff format`)
- Follow existing patterns

## Commands Quick Reference

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run optimized (minimal output)
uv run pytest -q --tb=short --disable-warnings

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run mypy src

# Export GraphQL schema
PYTHONPATH=src uv run python src/export_schema.py > schema.graphql
```

## Current Status

- ✅ **Planning**: Complete
- ✅ **Documentation**: Complete (Phase 1)
- 🔄 **Implementation**: Ready to start
- ⏳ **Phase 1**: Not started
- ⏳ **Phase 2-6**: Documentation pending

## Next Actions

1. **Review master plan**: Read [`00-index.md`](./00-index.md) in full
2. **Start Phase 1**: Begin with [`01-fix-session-filtering.md`](./01-fix-session-filtering.md)
3. **Create feature branch**: `git checkout -b feature/phase1-filtering`
4. **Assign to subagent**: Use template from task 01 document
5. **Track progress**: Update checklists as you complete items

## Questions?

- Review the detailed task documents for specific guidance
- Check the master index for overall context
- Each task includes troubleshooting and debugging tips
- Subagent templates include specific instructions for AI assistance

---

**Ready to begin?** Start with [Task 01: Fix Session Filtering](./01-fix-session-filtering.md)
