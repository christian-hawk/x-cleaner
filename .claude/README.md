# Claude Code Configuration for X-Cleaner

This directory contains Claude Code configuration, commands, and prompts specifically tailored for the X-Cleaner project.

## Structure

```
.claude/
├── claude.json              # Main configuration file
├── commands/                # Slash commands for common tasks
│   ├── quality-check.md     # Run code quality checks
│   ├── dev-start.md         # Start development servers
│   ├── test-run.md          # Run test suite
│   ├── architecture-review.md # Review architectural compliance
│   ├── scan-trigger.md      # Trigger X account scan
│   └── code-review.md       # Comprehensive code review
├── prompts/                 # Specialized prompts
│   └── implement-feature.md # Feature implementation guide
└── README.md               # This file
```

## Configuration Highlights

### Code Quality Standards (MANDATORY)
From `CODE_CONVENTIONS.md`:
- **Files**: ≤ 500 lines (MANDATORY REFACTOR if > 800)
- **Functions**: ≤ 60 lines (MANDATORY REFACTOR if > 100)
- **Complexity**: ≤ 10 (MANDATORY REFACTOR if > 15)
- **Naming**: EXTREMELY self-explanatory, NO abbreviations
- **Style**: PEP 8, line length 88, double quotes
- **Imports**: ALWAYS at top of file

### Architecture (4-Layer)
From `ARCHITECTURE.md`:
1. **Presentation**: Streamlit UI, CLI
2. **API**: FastAPI routes, WebSocket
3. **Business Logic**: Services, core logic
4. **Data**: Repositories, API clients

### Design Patterns
- Repository Pattern (data access)
- Service Layer (business logic)
- Factory Pattern (object creation)
- Strategy Pattern (swappable algorithms)
- Observer Pattern (WebSocket updates)
- Dependency Injection (loose coupling)

## Available Commands

Use slash commands in Claude Code:

### Development
- `/quality-check` - Run all code quality checks
- `/dev-start` - Start backend + frontend servers
- `/test-run` - Run tests with coverage
- `/scan-trigger` - Trigger new X account scan

### Review
- `/code-review` - Comprehensive code review checklist
- `/architecture-review` - Check architectural compliance

## Using Prompts

When implementing features, refer to:
- `/implement-feature` - Structured feature implementation guide

## Quick Reference

### Start Development
```bash
# Activate venv
source venv/bin/activate

# Start backend
uvicorn backend.main:app --reload --port 8000

# Start frontend (new terminal)
streamlit run streamlit_app/app.py
```

### Quality Check
```bash
# Format
black backend/ streamlit_app/
isort backend/ streamlit_app/

# Type check
mypy backend/

# Lint
pylint backend/

# Complexity
radon cc backend/ -a -nb

# Test
pytest --cov=backend
```

### Access
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs

## Key Files to Review
Before coding, always review:
1. **PROJECT_PLAN.md** - Feature requirements
2. **ARCHITECTURE.md** - Design patterns
3. **CODE_CONVENTIONS.md** - Quality standards (MANDATORY)
4. **IMPLEMENTATION_ROADMAP.md** - Code examples

## Testing Strategy
From `ARCHITECTURE.md`:
- **70% Unit tests** - Fast, isolated, mocked
- **20% Integration tests** - Real DB, mocked APIs
- **10% E2E tests** - Full system

**Coverage Goals:**
- Overall: ≥ 80%
- Core logic: ≥ 90%
- API clients: ≥ 85%
- Repositories: ≥ 85%

## Refactoring Triggers

Stop and refactor immediately when you see:
- 🚨 Function > 100 lines
- 🚨 File > 800 lines
- 🚨 Complexity > 15
- 🚨 Duplicate code in 2+ places
- 🚨 Abbreviations in names
- 🚨 Imports inside functions

## API Keys Required
In `.env`:
- `X_API_BEARER_TOKEN` - X API Basic Plan ($200/month)
- `XAI_API_KEY` - xAI Grok API
- `X_USER_ID` - Your X user ID

## Cost
- X API: $200/month (required)
- Grok API: ~$0.05 per 1000 accounts (negligible)
- **Total: ~$200/month**

## Support
For questions, refer to:
- Project docs in repo root
- API docs: http://localhost:8000/docs
- X API: https://developer.x.com
- xAI: https://docs.x.ai/
