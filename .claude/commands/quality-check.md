---
description: Run comprehensive code quality checks (formatting, linting, complexity, type checking)
---

Run a complete code quality check on the X-Cleaner project following the mandatory CODE_CONVENTIONS.md standards.

Check the following in order:

## 1. Code Formatting (Black)
```bash
black --check backend/ streamlit_app/
```
If formatting issues found, fix with: `black backend/ streamlit_app/`

## 2. Import Sorting (isort)
```bash
isort --check-only backend/ streamlit_app/
```
If issues found, fix with: `isort backend/ streamlit_app/`

## 3. Type Checking (mypy)
```bash
mypy backend/ --config-file .mypy.ini
```

## 4. Linting (pylint)
```bash
pylint backend/ --rcfile=.pylintrc
```

## 5. Cyclomatic Complexity (radon)
```bash
radon cc backend/ -a -nb --min C
```
❌ **FAIL if any function has complexity > 15**
⚠️  **WARN if any function has complexity > 10**

Check file sizes:
```bash
radon raw backend/ -s
```
❌ **FAIL if any file > 800 lines**
⚠️  **WARN if any file > 500 lines**

## 6. Code Maintainability
```bash
radon mi backend/ -s --min B
```

## Summary
Report:
- Total issues found
- Critical violations (complexity > 15, file > 800 lines)
- Warnings (complexity > 10, file > 500 lines)
- Next steps to fix

**Mandatory Standards from CODE_CONVENTIONS.md:**
- ✅ Files ≤ 500 lines (MANDATORY REFACTOR if > 800)
- ✅ Functions ≤ 60 lines (MANDATORY REFACTOR if > 100)
- ✅ Cyclomatic complexity ≤ 10 (MANDATORY REFACTOR if > 15)
- ✅ No abbreviations in names
- ✅ All imports at top of file
- ✅ Type hints on all function signatures
