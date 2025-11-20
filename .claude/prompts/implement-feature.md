# Feature Implementation Prompt

When implementing a new feature for X-Cleaner, follow this structured approach:

## Context
- Review **PROJECT_PLAN.md** for feature requirements
- Review **ARCHITECTURE.md** for design patterns to use
- Review **CODE_CONVENTIONS.md** for code quality standards (MANDATORY)
- Review **IMPLEMENTATION_ROADMAP.md** for code examples

## Implementation Steps

### 1. Design Phase
Before writing code, design:
- Data models (Pydantic schemas)
- Database schema (if needed)
- API endpoints (REST + WebSocket if real-time)
- Service layer methods
- Repository methods (if data access needed)

### 2. Implementation Order
Implement bottom-up (Data → Business → API → Presentation):

**a. Data Layer:**
- Create/update SQLAlchemy models
- Create/update repository methods
- Add database migrations if needed

**b. Business Logic Layer:**
- Implement service methods
- Add business logic and validation
- Handle errors with custom exceptions

**c. API Layer:**
- Create FastAPI route handlers
- Define request/response models (Pydantic)
- Add WebSocket handlers if real-time needed
- Use dependency injection (Depends)

**d. Presentation Layer:**
- Add Streamlit UI components
- Connect to backend API
- Handle loading states and errors

### 3. Code Quality Requirements (MANDATORY)

**Naming (EXTREMELY self-explanatory):**
- Classes: PascalCase nouns (AccountRepository, ScanService)
- Functions: snake_case verbs (fetch_following, categorize_accounts)
- Variables: snake_case descriptive (discovered_categories, categorized_accounts_list)
- ❌ FORBIDDEN: Abbreviations (usr, acc, cat), single letters (except i,j,k,e,_), vague names (data, temp, info)

**Size Limits:**
- Files: ≤ 500 lines (MANDATORY REFACTOR if > 800)
- Functions: ≤ 60 lines (MANDATORY REFACTOR if > 100)
- Cyclomatic Complexity: ≤ 10 (MANDATORY REFACTOR if > 15)

**Code Style:**
- PEP 8 (line length 88)
- All imports at TOP of file (after docstring)
- Type hints on ALL function signatures
- Docstrings for all public functions/classes (Google style)
- Double quotes for strings

**Principles:**
- DRY: NEVER duplicate logic
- Self-documenting: Names so clear that comments are unnecessary
- SOLID: Follow all 5 principles
- Use design patterns: Repository, Service Layer, Dependency Injection

### 4. Testing Requirements

Write tests in this order:
1. **Unit tests** (70%): Test services/repositories in isolation with mocks
2. **Integration tests** (20%): Test with real database, mocked external APIs
3. **E2E tests** (10%): Test full workflow

**Coverage Goals:**
- Overall: ≥ 80%
- Core business logic: ≥ 90%
- API clients: ≥ 85%
- Repositories: ≥ 85%

### 5. Documentation
Update:
- API documentation (docstrings → auto-generated Swagger)
- README.md if user-facing feature
- Add examples in implementation guide

### 6. Quality Checklist
Before submitting:
```bash
# Format
black backend/ streamlit_app/
isort backend/ streamlit_app/

# Type check
mypy backend/

# Lint
pylint backend/

# Complexity check
radon cc backend/ -a -nb --min C

# Tests
pytest --cov=backend --cov-report=term
```

## Example Implementation Template

```python
# backend/core/services/example_service.py
"""Service for example feature.

This module provides business logic for the example feature,
orchestrating data access and external API calls.
"""

from typing import List, Optional
from backend.db.repositories.example_repository import ExampleRepository
from backend.api.external_client import ExternalClient
from backend.exceptions import ExampleError


class ExampleService:
    """Service for example feature business logic."""

    def __init__(
        self,
        example_repository: ExampleRepository,
        external_client: ExternalClient
    ):
        """Initialize service with dependencies.

        Args:
            example_repository: Repository for data access.
            external_client: Client for external API calls.
        """
        self._example_repository = example_repository
        self._external_client = external_client

    async def perform_example_operation(
        self,
        example_input: str,
        optional_parameter: Optional[int] = None
    ) -> List[dict]:
        """Perform example business operation.

        Args:
            example_input: The input for the operation.
            optional_parameter: Optional parameter for customization.

        Returns:
            List of result dictionaries.

        Raises:
            ExampleError: If operation fails.
        """
        # Validate input
        if not example_input:
            raise ExampleError(
                "Example input cannot be empty",
                details={"input": example_input}
            )

        # Fetch data from external API
        try:
            external_data = await self._external_client.fetch_data(example_input)
        except ExternalAPIError as error:
            raise ExampleError(
                f"Failed to fetch external data: {error}",
                details={"input": example_input}
            ) from error

        # Process data (business logic)
        processed_data = self._process_external_data(
            external_data,
            optional_parameter
        )

        # Save to database
        saved_results = self._example_repository.save_batch(processed_data)

        return saved_results

    def _process_external_data(
        self,
        external_data: List[dict],
        optional_parameter: Optional[int]
    ) -> List[dict]:
        """Process external data (private helper method).

        Args:
            external_data: Raw data from external API.
            optional_parameter: Optional processing parameter.

        Returns:
            Processed data ready for storage.
        """
        # Processing logic here
        processed_results = []

        for data_item in external_data:
            processed_item = {
                "id": data_item["id"],
                "value": data_item["value"] * (optional_parameter or 1),
                "processed": True
            }
            processed_results.append(processed_item)

        return processed_results
```

## Remember
- **Quality over speed**: Take time to write clean, maintainable code
- **Test first**: Consider TDD approach
- **Refactor ruthlessly**: Don't tolerate code smells
- **Review thoroughly**: Use code review checklist
- **Document clearly**: Future you will thank you
