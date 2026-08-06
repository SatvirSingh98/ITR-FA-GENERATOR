# Archive - Legacy Code

This directory contains the original monolithic implementation before the Phase 1 & 2 refactoring.

## Files

- **itr_fa_etrade.py** (3,508 lines) - Original monolithic script
  - All functionality in one file
  - Working, but difficult to maintain and debug
  - Kept for reference only

## Why Archived?

The codebase was refactored into 14 modular components for better:
- **Maintainability** - Each module handles one responsibility
- **Debuggability** - Easy to find and fix issues
- **Extensibility** - Easy to add new features
- **Testability** - Isolated components can be tested independently

## Current Architecture

See `scripts/etrade/` for the modular implementation:
- 14 focused modules (~221 lines each)
- Clear separation of concerns
- Full test coverage
- Same functionality, better structure

**DO NOT USE** the archived script for production. Use the modular version via `GENERATE_ITR_FA.bat`.
