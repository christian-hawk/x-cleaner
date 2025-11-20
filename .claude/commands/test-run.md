---
description: Run project test suite with coverage reporting
---

Run comprehensive tests for X-Cleaner following the testing strategy from ARCHITECTURE.md.

## Quick Test Run

Run all tests:
```bash
pytest tests/ -v
```

## Test with Coverage

Run tests with coverage report:
```bash
pytest tests/ --cov=backend --cov=streamlit_app --cov-report=html --cov-report=term-missing
```

**Coverage Goals (from ARCHITECTURE.md):**
- Overall: ≥ 80%
- Core business logic (backend/core/): ≥ 90%
- API clients (backend/api/): ≥ 85%
- Repositories (backend/db/repositories/): ≥ 85%

## Test by Category

**Unit tests only (fast):**
```bash
pytest tests/unit/ -v
```

**Integration tests:**
```bash
pytest tests/integration/ -v
```

**End-to-end tests:**
```bash
pytest tests/e2e/ -v
```

**Async tests only:**
```bash
pytest tests/ -v -m asyncio
```

## Test Specific Module

```bash
# Test X API client
pytest tests/unit/api/test_x_client.py -v

# Test Grok client
pytest tests/unit/api/test_grok_client.py -v

# Test categorization
pytest tests/unit/core/test_categorizer.py -v

# Test scanner
pytest tests/unit/core/test_scanner.py -v
```

## Coverage Report Location

After running with `--cov-report=html`, open:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Quality Checks

Ensure all tests follow best practices:
- ✅ Use Arrange-Act-Assert pattern
- ✅ Use fixtures for dependencies
- ✅ Mock external API calls
- ✅ Use descriptive test names (test_<action>_<expected_result>)
- ✅ One assertion per test (when possible)
- ✅ Use @pytest.mark.asyncio for async tests

## Continuous Testing

Watch mode (re-run on file changes):
```bash
pytest-watch tests/ backend/
```

## Generate Coverage Badge

```bash
coverage-badge -o coverage.svg -f
```
