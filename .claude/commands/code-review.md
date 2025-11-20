---
description: Perform code review checklist from CODE_CONVENTIONS.md on recent changes
---

Perform a comprehensive code review following the mandatory checklist from CODE_CONVENTIONS.md.

## Review Checklist

### 1. Readability ✅
```bash
# Review recent changes
git diff main --name-only | grep ".py$"
```

For each file, check:
- [ ] All variable/function names are EXTREMELY self-explanatory
- [ ] No abbreviations used (usr, acc, cat, etc.)
- [ ] No single-letter variables (except i, j, k, e, _)
- [ ] Comments only where absolutely necessary
- [ ] Code reads like prose

**Anti-patterns to look for:**
```bash
# Search for common abbreviations
grep -E "\b(usr|acc|cat|msg|cfg|ctx|req|res|auth|util|mgr|svc)\b" backend/**/*.py

# Search for vague names
grep -E "\b(data|temp|info|value|result|item|obj)\s*=" backend/**/*.py
```

### 2. DRY (Don't Repeat Yourself) ✅
```bash
# Use similarity detection
pylint backend/ --disable=all --enable=duplicate-code
```

Check:
- [ ] No duplicated logic
- [ ] Repeated code extracted into functions
- [ ] No copy-paste code

### 3. Size Limits ✅
```bash
# Check file sizes
radon raw backend/ streamlit_app/ -s | grep -E "LOC|LLOC"

# Check function sizes
radon cc backend/ -s -a | grep -E "F:|M:"

# Check complexity
radon cc backend/ -a -nb --min C
```

Verify:
- [ ] All files ≤ 800 lines (ideally ≤ 500)
- [ ] All functions ≤ 100 lines (ideally ≤ 60)
- [ ] Cyclomatic complexity ≤ 15 (ideally ≤ 10)

### 4. PEP 8 Compliance ✅
```bash
# Auto-format check
black --check backend/ streamlit_app/

# Import sorting check
isort --check-only backend/ streamlit_app/
```

Verify:
- [ ] All imports at top of file
- [ ] Imports properly ordered (stdlib, 3rd-party, local)
- [ ] Line length ≤ 88 characters
- [ ] Proper spacing and indentation
- [ ] Double quotes for strings

### 5. Quality Standards ✅
```bash
# Type checking
mypy backend/ --disallow-untyped-defs

# Find missing docstrings
pylint backend/ --disable=all --enable=missing-docstring
```

Verify:
- [ ] Type hints on all function signatures
- [ ] Docstrings for all public functions/classes
- [ ] Guard clauses instead of deep nesting
- [ ] Early returns to reduce complexity
- [ ] Specific exception handling (no bare `except`)

### 6. Design Patterns ✅

**Repository Pattern:**
- [ ] All DB operations through repositories
- [ ] Repositories have no business logic
- [ ] Repositories return domain models, not DB models

**Service Layer:**
- [ ] Business logic in services, not routes
- [ ] Services orchestrate repositories and clients
- [ ] Services are reusable across CLI/API/Web

**Dependency Injection:**
- [ ] FastAPI routes use Depends()
- [ ] No global state (except config)
- [ ] Services receive dependencies in constructor

### 7. Testing ✅
```bash
# Check test coverage
pytest --cov=backend --cov-report=term-missing
```

Verify:
- [ ] Unit tests for new functions
- [ ] Edge cases covered
- [ ] Error cases tested
- [ ] Coverage ≥ 80% overall
- [ ] Coverage ≥ 90% for core business logic

### 8. Architecture Compliance ✅

Check layer separation:
```bash
# No cross-layer imports
grep -r "from streamlit_app" backend/core/
grep -r "from backend.core" backend/db/
```

Verify:
- [ ] Presentation → API → Business → Data (no skipping)
- [ ] No circular dependencies
- [ ] Clear separation of concerns

### 9. Security & Privacy ✅

Check for:
- [ ] No hardcoded secrets
- [ ] No sensitive data in logs
- [ ] Proper input validation
- [ ] SQL injection prevention (using ORM)
- [ ] Rate limiting on API endpoints

```bash
# Search for potential secrets
grep -ri "api.*key.*=.*['\"]" backend/ | grep -v ".env"
grep -ri "token.*=.*['\"]" backend/ | grep -v ".env"
```

### 10. Error Handling ✅

Verify:
- [ ] Specific exceptions caught (not bare `except`)
- [ ] Exceptions have context (details dict)
- [ ] Failed operations logged with ERROR level
- [ ] User-friendly error messages

```bash
# Check for bare except
grep -r "except:" backend/ --include="*.py"
```

## Automated Review

Run all automated checks:
```bash
# Format
black backend/ streamlit_app/
isort backend/ streamlit_app/

# Lint
pylint backend/
mypy backend/

# Complexity
radon cc backend/ -a -nb
radon mi backend/ -s

# Tests
pytest --cov=backend --cov-report=term
```

## Manual Review Focus Areas

1. **Function naming**: Does it clearly describe what it does?
2. **Variable naming**: Can you understand what it contains without context?
3. **Logic clarity**: Can you follow the flow without comments?
4. **Error handling**: Are edge cases handled?
5. **Performance**: Any obvious inefficiencies?
6. **Security**: Any potential vulnerabilities?

## Review Sign-off

After review, verify:
- [ ] All automated checks pass
- [ ] All manual checks complete
- [ ] No blockers found
- [ ] Code meets quality standards

✅ **APPROVED FOR MERGE**
or
❌ **CHANGES REQUESTED** (list specific issues)
