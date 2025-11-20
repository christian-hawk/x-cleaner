---
description: Set up development tools and configurations for code quality
---

Set up all development tools and configurations for the X-Cleaner project to enforce code quality standards.

## Prerequisites

Ensure virtual environment is activated:
```bash
which python  # Should show venv path
```

## Install Development Tools

```bash
# Code formatting
pip install black isort

# Type checking
pip install mypy

# Linting
pip install pylint

# Code complexity analysis
pip install radon

# Testing
pip install pytest pytest-cov pytest-asyncio pytest-watch

# Additional dev tools
pip install ipython ipdb
```

Or install all at once:
```bash
pip install -r requirements-dev.txt
```

## Verify Installations

```bash
black --version
isort --version
mypy --version
pylint --version
radon --version
pytest --version
```

## Configuration Files

The following configuration files should already exist:

### `.mypy.ini` - Type Checking Configuration
```ini
[mypy]
python_version = 3.11
disallow_untyped_defs = True
disallow_incomplete_defs = True
# ... (see .mypy.ini)
```

### `.pylintrc` - Linting Configuration
```ini
[MASTER]
jobs=4

[DESIGN]
max-args=5
max-locals=15
# ... (see .pylintrc)
```

### `pyproject.toml` - Black & isort Configuration
```toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 88
```

### `pytest.ini` - Testing Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Create Missing Config Files

If any config files are missing, create them:

### Create `pyproject.toml`:
```bash
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | venv
  | dist
  | build
)/
'''

[tool.isort]
profile = "black"
line_length = 88
skip_gitignore = true
known_first_party = ["backend", "streamlit_app"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = "-v --strict-markers"
markers = [
    "asyncio: mark test as async",
    "unit: mark test as unit test",
    "integration: mark test as integration test",
    "e2e: mark test as end-to-end test"
]
EOF
```

### Create `pytest.ini` (alternative to pyproject.toml):
```bash
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    asyncio: mark test as async
    unit: mark test as unit test
    integration: mark test as integration test
    e2e: mark test as end-to-end test
EOF
```

### Create `requirements-dev.txt`:
```bash
cat > requirements-dev.txt << 'EOF'
# Code formatting
black>=24.0.0
isort>=5.13.0

# Type checking
mypy>=1.8.0
types-requests
types-python-dotenv

# Linting
pylint>=3.0.0

# Code quality
radon>=6.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-watch>=4.2.0
pytest-mock>=3.12.0

# Development tools
ipython>=8.12.0
ipdb>=0.13.0

# Documentation
sphinx>=7.2.0
sphinx-rtd-theme>=2.0.0
EOF
```

## Pre-commit Hooks (Optional)

Set up pre-commit hooks to automatically check code before commits:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```bash
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--config-file=.mypy.ini]

  - repo: https://github.com/pycqa/pylint
    rev: v3.0.3
    hooks:
      - id: pylint
        args: [--rcfile=.pylintrc]
EOF
```

Install hooks:
```bash
pre-commit install
```

## IDE Configuration

### VS Code (`.vscode/settings.json`)
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.rulers": [88],
    "editor.tabSize": 4
  }
}
```

### PyCharm
1. Settings → Tools → Black → Enable
2. Settings → Tools → External Tools → Add mypy
3. Settings → Editor → Code Style → Python → Line length: 88
4. Settings → Editor → Inspections → Enable type hints

## Verify Setup

Run all tools to verify setup:

```bash
# Format check
black --check backend/ streamlit_app/
isort --check-only backend/ streamlit_app/

# Type check
mypy backend/

# Lint
pylint backend/

# Complexity
radon cc backend/ -a -nb

# Tests
pytest --version
```

If all commands run without errors, setup is complete! ✅

## Next Steps

1. Run quality check: `/quality-check`
2. Start development: `/dev-start`
3. Begin coding with confidence knowing quality is enforced
