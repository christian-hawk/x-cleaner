---
description: Review code against architectural patterns and design principles from ARCHITECTURE.md
---

Perform a comprehensive architectural review of the X-Cleaner codebase to ensure compliance with ARCHITECTURE.md.

## 1. Layer Separation Check

Verify 4-layer architecture is maintained:
- **Presentation Layer**: `streamlit_app/`, `backend/cli/`
- **API Layer**: `backend/routes/`, `backend/api/`
- **Business Logic Layer**: `backend/core/`
- **Data Layer**: `backend/db/`, `backend/api/x_client.py`, `backend/api/grok_client.py`

**Check for violations:**
- ❌ Presentation importing from Data layer (skipping API/Business)
- ❌ Business Logic importing from Presentation
- ❌ Data layer depending on upper layers

Search for anti-patterns:
```bash
# Check if streamlit imports from db directly
grep -r "from backend.db" streamlit_app/

# Check if core imports from streamlit
grep -r "from streamlit_app" backend/core/

# Check if db imports from core
grep -r "from backend.core" backend/db/
```

## 2. Design Pattern Compliance

**Repository Pattern:**
- Check that all database operations go through repositories
- Repositories should ONLY perform database operations
- No business logic in repositories

Files to review:
```bash
ls backend/db/repositories/
```

**Service Layer Pattern:**
- Check that business logic is in services
- Services orchestrate repositories and API clients
- Services are reusable across CLI, API, and web UI

Files to review:
```bash
ls backend/core/services/
```

**Dependency Injection:**
- Check FastAPI routes use Depends()
- Check services receive dependencies via constructor
- No global state or singletons (except config)

```bash
grep -r "Depends(" backend/routes/
```

## 3. Naming Convention Audit

**Check for forbidden patterns:**

Abbreviations (FORBIDDEN):
```bash
grep -r "\busr\b" backend/ streamlit_app/ --include="*.py" | grep -v "# " | grep -v "user"
grep -r "\bacc\b" backend/ streamlit_app/ --include="*.py" | grep -v "# " | grep -v "account"
grep -r "\bcat\b" backend/ streamlit_app/ --include="*.py" | grep -v "# " | grep -v "category"
```

Single letter variables (except i, j, k, e, _):
```bash
# This is harder to grep, do manual code review
```

Vague names (FORBIDDEN):
```bash
grep -r "def.*manager" backend/ --include="*.py"
grep -r "def.*handler" backend/ --include="*.py"
grep -r "data\s*=" backend/ --include="*.py"
grep -r "temp\s*=" backend/ --include="*.py"
```

## 4. Import Organization Check

All imports at top of file?
```bash
# Search for imports inside functions (should be rare)
grep -A 5 "^def " backend/**/*.py | grep "import "
```

## 5. Type Hints Coverage

Check that all functions have type hints:
```bash
# Run mypy in strict mode
mypy backend/ --disallow-untyped-defs
```

## 6. Error Handling Review

Check exception hierarchy compliance:
```bash
# Should have custom exceptions
cat backend/exceptions.py

# Check if routes catch specific exceptions
grep -r "except Exception" backend/routes/
# Should be minimal - catch specific exceptions instead
```

## 7. Logging Strategy Review

Check structured logging is used:
```bash
grep -r "logger\." backend/ --include="*.py" | head -20
```

Verify:
- ✅ Using logger, not print()
- ✅ Appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ✅ Structured fields via extra={}
- ❌ No sensitive data logged

## 8. Configuration Management

Check all config in one place:
```bash
cat backend/config.py
```

Verify:
- ✅ Using Pydantic BaseSettings
- ✅ All settings from environment variables
- ✅ Type hints on all settings
- ✅ Default values where appropriate

## Summary Report

Generate a summary:
1. Layer violations found: X
2. Missing design patterns: Y
3. Naming convention violations: Z
4. Type hint coverage: N%
5. Test coverage: M%

**Architecture Health Score:** (100 - violations) / 100
