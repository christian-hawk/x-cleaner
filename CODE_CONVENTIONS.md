# Code Conventions & Style Guide

**Objetivo**: Código extremamente legível, manutenível e de alta qualidade.

---

## 🎯 CLEAN CODE PRINCIPLES (MANDATORY)

**Code is read far more often than it is written. Optimize for readability above all else.**

### SOLID Principles (Uncle Bob)

- **S - Single Responsibility Principle**: One class = one reason to change
- **O - Open/Closed Principle**: Open for extension, closed for modification
- **L - Liskov Substitution Principle**: Subtypes must be substitutable for base types
- **I - Interface Segregation Principle**: Many specific interfaces > one general interface
- **D - Dependency Inversion Principle**: Depend on abstractions, not concretions

### Function Principles

- **Do ONE thing**: Function should do one thing only
- **One level of abstraction**: Don't mix high/low level operations
- **Stepdown Rule**: Code reads like top-to-bottom narrative
- **Command Query Separation**: Function either does something OR returns something
- **No flag arguments**: Boolean parameters = code smell
- **Extract try/catch blocks**: Error handling is ONE thing

### Error Handling Principles

- **Use exceptions, not return codes**
- **Don't return None**: Raise exception or return empty object
- **Don't pass None**: Validate parameters
- **Provide actionable context**: Exception messages must be clear

### Law of Demeter

- **Don't talk to strangers**: Only talk to immediate friends
- **Avoid train wrecks**: `a.getB().getC()` is bad

### Simple Design (Kent Beck)

1. Passes all tests
2. No duplication
3. Expresses intent clearly
4. Minimizes classes and methods

### DRY Principle (Don't Repeat Yourself)
- ❌ **NEVER** duplicate logic
- ✅ Extract repeated code into reusable functions/classes
- ✅ Use inheritance, composition, or utility functions
- If you copy-paste code, STOP and refactor

```python
# ❌ BAD - Duplicated logic
def unfollow_category(category_name):
    accounts = get_accounts(category_name)
    for account in accounts:
        try:
            api_client.unfollow(account.id)
            logger.info(f"Unfollowed {account.username}")
        except Exception as e:
            logger.error(f"Failed to unfollow {account.username}: {e}")

def unfollow_bulk(account_ids):
    for account_id in account_ids:
        try:
            api_client.unfollow(account_id)
            logger.info(f"Unfollowed {account_id}")
        except Exception as e:
            logger.error(f"Failed to unfollow {account_id}: {e}")

# ✅ GOOD - DRY with extracted function
def _unfollow_single_account(account_id: str, username: str = None) -> bool:
    """Unfollow single account with error handling."""
    try:
        api_client.unfollow(account_id)
        display_name = username or account_id
        logger.info(f"Unfollowed {display_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to unfollow {display_name}: {e}")
        return False

def unfollow_category(category_name: str) -> UnfollowResult:
    accounts = get_accounts(category_name)
    return [_unfollow_single_account(acc.id, acc.username) for acc in accounts]

def unfollow_bulk(account_ids: List[str]) -> UnfollowResult:
    return [_unfollow_single_account(acc_id) for acc_id in account_ids]
```

### Self-Documenting Code

- ✅ Variable and function names must be **EXTREMELY self-explanatory**
- ✅ Anyone reading the code should understand it **WITHOUT comments**
- ❌ Avoid abbreviations: `usr` → `user`, `acc` → `account`, `cat` → `category`
- ❌ Avoid single letters except for: `i`, `j`, `k` (loops), `e` (exceptions)

```python
# ❌ BAD - Comments explaining what code does
def process_data(d):
    # Get the user id from the dictionary
    uid = d.get("id")
    # Check if user id exists
    if uid:
        # Process the user id
        return process_uid(uid)

# ✅ GOOD - Self-documenting code, no comments needed
def extract_and_process_user_id(user_data: dict) -> Optional[ProcessedUser]:
    user_id = user_data.get("id")
    if not user_id:
        return None
    return process_user_id(user_id)
```

### Comments (A Necessary Evil)

- ⚠️ **Comments are a code smell** - they indicate the code isn't clear enough
- ✅ Use comments ONLY for:
  - Complex algorithms that can't be simplified
  - Business logic WHY (not WHAT or HOW)
  - Workarounds for external API quirks
  - Performance optimization explanations
- ❌ **NEVER** comment obvious code
- ❌ **NEVER** use comments to explain bad variable names → rename instead

```python
# ✅ GOOD COMMENTS - Explain WHY, not WHAT

# Rate limit: X API allows 50 unfollows per 15 minutes
# We add 1.2s delay between requests to stay under this limit
await asyncio.sleep(UNFOLLOW_RATE_LIMIT_DELAY_SECONDS)

# Workaround: Grok API sometimes returns malformed JSON
# for very long category descriptions. Truncate to 500 chars.
description = description[:500]

# Performance: Cache categorization results for 24h to avoid
# redundant API calls. Categories rarely change.
@cache(ttl=86400)
def get_account_categories():
    pass

# ❌ BAD COMMENTS - Explain WHAT (obvious from code)

# Increment counter
counter += 1

# Get the username
username = account.username

# Loop through accounts
for account in accounts:
    pass

# Check if user exists
if user:
    pass
```

---

## 📏 Code Size Limits

### Files

- ✅ **Desirable**: ≤ 500 lines
- ⚠️ **Warning**: 500-800 lines (consider splitting)
- 🚨 **MANDATORY REFACTOR**: > 800 lines

**When file exceeds 800 lines:**
- Split into multiple modules by responsibility
- Extract related classes into separate files
- Move utilities to `utils/` directory

### Functions/Methods

- ✅ **Desirable**: ≤ 60 lines
- ⚠️ **Warning**: 60-100 lines (consider splitting)
- 🚨 **MANDATORY REFACTOR**: > 100 lines

**When function exceeds 100 lines:**
- Extract sub-functions for logical steps
- Use composition over long procedures
- Consider if function has too many responsibilities (SRP violation)

### Cyclomatic Complexity

- ✅ **Maximum Allowed**: 15
- ✅ **Target**: ≤ 10
- 🚨 If complexity > 15: **MANDATORY REFACTOR** - split into smaller functions

**Cyclomatic Complexity** = Number of independent paths through code
- Each `if`, `elif`, `for`, `while`, `and`, `or`, `except` adds +1
- High complexity = hard to test, hard to understand, more bugs

### How to Measure

```bash
# Install radon
pip install radon

# Check cyclomatic complexity
radon cc backend/ -a -nb

# Check maintainability index
radon mi backend/ -s

# Check lines of code
radon raw backend/ -s

# Full report
radon cc backend/ -a -s && radon mi backend/ -s
```

**Interpreting Results:**
- Complexity 1-5: ✅ Simple
- Complexity 6-10: ✅ Good
- Complexity 11-15: ⚠️ Warning (consider refactoring)
- Complexity 16+: 🚨 High risk (mandatory refactor)

---

## 🚨 Refactoring Triggers

When you see any of these, STOP and refactor immediately:

| Trigger | Action |
|---------|--------|
| 🚨 Function > 100 lines | Extract sub-functions |
| 🚨 File > 800 lines | Split into multiple modules |
| 🚨 Cyclomatic complexity > 15 | Simplify logic, extract functions |
| 🚨 Duplicate code in 2+ places | Create shared function/class |
| 🚨 Function with > 5 parameters | Use object/dataclass/kwargs |
| 🚨 Nested if/else > 3 levels | Use early returns, guard clauses, strategy pattern |
| 🚨 Try/except catching generic Exception | Catch specific exceptions |
| 🚨 Class with > 10 methods | Split responsibilities (SRP) |

### Refactoring Example: Complex Nested Logic

```python
# ❌ BAD - Too complex, nested, hard to read (Complexity: 18)
def process_account(account, categories, min_confidence, retry_count, use_cache):
    if account:
        if account.is_active:
            if categories:
                if len(categories) > 0:
                    for category in categories:
                        if category.confidence > min_confidence:
                            if use_cache:
                                cached = get_cache(account.id)
                                if cached:
                                    return cached
                            result = categorize(account, category)
                            if result:
                                if retry_count > 0:
                                    return result
    return None

# ✅ GOOD - Clean, early returns, readable (Complexity: 5)
def process_account_categorization(
    account: Account,
    categories: List[Category],
    min_confidence: float,
    use_cache: bool = True
) -> Optional[CategorizationResult]:
    """Process account categorization with confidence threshold."""

    # Guard clauses (early returns)
    if not account or not account.is_active:
        return None

    if not categories:
        return None

    # Check cache first
    if use_cache:
        cached_result = get_cached_categorization(account.id)
        if cached_result:
            return cached_result

    # Find best matching category
    valid_categories = _filter_categories_by_confidence(categories, min_confidence)
    if not valid_categories:
        return None

    return categorize_account(account, valid_categories)

def _filter_categories_by_confidence(
    categories: List[Category],
    min_confidence: float
) -> List[Category]:
    """Filter categories above confidence threshold."""
    return [c for c in categories if c.confidence > min_confidence]
```

---

## 📝 PEP 8 Style Guide

**Base Standard**: **PEP 8** (MANDATORY - no exceptions without justification)

### Line Length

- **Maximum**: 88 characters (Black formatter default)
- Break long lines using parentheses or backslashes
- Prefer breaking after operators

```python
# ✅ GOOD
result = (
    very_long_function_name(argument1, argument2, argument3)
    + another_function(argument4, argument5)
    + yet_another_function(argument6)
)

# ✅ GOOD
if (
    condition_one
    and condition_two
    and condition_three
):
    do_something()
```

### Imports

**Location**: **ALWAYS at the top of the file** (after module docstring)
- ❌ **NEVER** import inside functions (except for circular dependency workarounds)
- ❌ **NEVER** import in the middle of the file
- ✅ All imports at the top, properly organized

**Order** (MANDATORY):
1. Standard library imports
2. Third-party library imports
3. Local application imports

**Within each group**: Alphabetical order

```python
"""Module for scanning X accounts.

This module provides functionality for scanning and analyzing
accounts that a user follows on X (Twitter).
"""

# 1. Standard library
import asyncio
import os
from datetime import datetime
from typing import List, Optional, Dict

# 2. Third-party libraries
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 3. Local application
from backend.api.x_client import XClient
from backend.core.scanner import Scanner
from backend.db.models import Account
from backend.db.repositories.account_repository import AccountRepository
```

### Whitespace

```python
# ✅ GOOD - Proper spacing
result = function(arg1, arg2, arg3)
my_list = [1, 2, 3, 4]
my_dict = {"key": "value", "foo": "bar"}

if x == 4:
    print(x, y)

# ❌ BAD - Inconsistent spacing
result=function(arg1,arg2,arg3)
my_list=[1,2,3,4]
if x==4:
    print (x,y)
```

---

## 🏷️ Naming Conventions (MANDATORY)

**Golden Rule**: Names must be so clear that comments become unnecessary.

### Classes: PascalCase

Nouns describing what the class represents.

```python
# ✅ GOOD
class AccountRepository:
    """Repository for managing account data persistence."""
    pass

class XApiClient:
    """Client for X (Twitter) API v2."""
    pass

class UnfollowService:
    """Service for managing bulk unfollow operations."""
    pass

# ❌ BAD
class XClient:  # Unclear: what does X mean?
    pass

class Manager:  # Too vague: manages what?
    pass

class Utils:  # Anti-pattern: utility dumping ground
    pass
```

### Functions/Methods: snake_case

Verbs describing what they do.

```python
# ✅ GOOD - Clear action verbs
def scan_accounts() -> List[Account]:
    pass

def get_user_following_accounts_with_metadata(user_id: str) -> List[Account]:
    pass

def calculate_category_distribution_percentage(category: str) -> float:
    pass

def unfollow_account_by_id(account_id: str) -> bool:
    pass

# ❌ BAD - Too vague or unclear
def process():  # Process WHAT?
    pass

def handle_data():  # Handle WHAT data? HOW?
    pass

def do_stuff():  # Completely meaningless
    pass

def proc_acc():  # Abbreviations - FORBIDDEN
    pass
```

### Variables: snake_case

EXTREMELY descriptive - explain exactly what the variable contains.

```python
# ✅ GOOD - Crystal clear
total_accounts_scanned = 847
unfollowed_account_count = 23
failed_account_ids = []
authenticated_user_id = "12345"
categorization_confidence_threshold = 0.7
rate_limit_delay_seconds = 1.2

# ❌ BAD - Abbreviations or vague
acc = 847  # FORBIDDEN - abbreviation
x = 23  # FORBIDDEN - meaningless
data = []  # Too vague - what data?
temp = 1.2  # Temporary what?
cfg = {}  # FORBIDDEN - abbreviation
```

### Constants: UPPER_SNAKE_CASE

Describe the value's purpose and context.

```python
# ✅ GOOD
MAX_RETRY_ATTEMPTS = 3
X_API_BASE_URL = "https://api.x.com"
GROK_API_RATE_LIMIT_PER_MINUTE = 60
UNFOLLOW_RATE_LIMIT_DELAY_SECONDS = 1.2
DEFAULT_CATEGORIZATION_CONFIDENCE_THRESHOLD = 0.7
DATABASE_CONNECTION_TIMEOUT_SECONDS = 30

# ❌ BAD
MAX = 3  # Max what?
URL = "https://api.x.com"  # Which URL?
LIMIT = 60  # What kind of limit?
DELAY = 1.2  # Delay for what?
```

### Boolean Variables

Start with `is_`, `has_`, `should_`, `can_`, `will_`

```python
# ✅ GOOD
is_account_active = True
has_valid_credentials = False
should_retry_on_failure = True
can_unfollow_account = True
will_use_cache = True
is_rate_limited = False

# ❌ BAD
active = True  # Not clear it's boolean
valid = False  # Valid what?
retry = True  # Ambiguous
cache = True  # Noun, not boolean
```

### Private Members: Leading Underscore

```python
class Scanner:
    def __init__(self):
        # ✅ Private instance variables
        self._rate_limiter = RateLimiter()
        self._authenticated_user_id = None
        self._cache = {}

    # ✅ Private helper method
    def _fetch_batch(self, cursor: str) -> List[Account]:
        pass

    # ✅ Public API method
    def scan_accounts(self, user_id: str) -> List[Account]:
        return self._fetch_batch(cursor=None)
```

### Type Aliases: PascalCase

Describe the type's semantic meaning.

```python
# ✅ GOOD
AccountList = List[Account]
CategoryMapping = Dict[str, List[Account]]
UnfollowCallback = Callable[[int, int, str], None]
ScanProgressHandler = Callable[[float], Awaitable[None]]

# ❌ BAD
MyList = List[Account]  # Not descriptive
Data = Dict[str, Any]  # Too vague
Func = Callable  # Unclear purpose
```

---

## 🚫 Naming Anti-Patterns (FORBIDDEN)

### Single Letter Variables

❌ **FORBIDDEN** except for:
- `i`, `j`, `k` in simple loops
- `e` for exceptions
- `_` for intentionally unused values

```python
# ✅ ACCEPTABLE
for i in range(10):
    print(i)

for i, account in enumerate(accounts):
    print(f"{i}: {account.username}")

try:
    risky_operation()
except ValueError as e:
    logger.error(f"Value error: {e}")

# ✅ GOOD - Better than single letters
for account_index, account in enumerate(accounts):
    process_account(account)

# ❌ FORBIDDEN
a = get_account()
x = calculate()
d = {"key": "value"}
```

### Abbreviations

❌ **COMPLETELY FORBIDDEN**

```python
# ❌ FORBIDDEN
usr = get_user()
acc = get_account()
cat = get_category()
msg = "Hello"
cfg = load_config()
auth = authenticate()
repo = AccountRepository()
svc = ScanService()

# ✅ CORRECT
user = get_user()
account = get_account()
category = get_category()
message = "Hello"
config = load_config()
authenticator = authenticate()
repository = AccountRepository()
service = ScanService()
```

### Numbers in Names

❌ **FORBIDDEN** (except when semantically meaningful)

```python
# ❌ BAD
account1 = fetch_account()
account2 = fetch_another_account()
result1 = process()
result2 = process_again()

# ✅ GOOD
primary_account = fetch_primary_account()
secondary_account = fetch_secondary_account()
categorization_result = categorize_account()
validation_result = validate_account()

# ✅ ACCEPTABLE - Semantically meaningful
http_status_code_200 = 200
api_v2_endpoint = "/api/v2/accounts"
```

### Vague Names

❌ **FORBIDDEN**

```python
# ❌ FORBIDDEN - Too vague
data = fetch()
info = get()
temp = calculate()
result = process()
value = compute()
item = get_item()

# ✅ CORRECT - Specific
account_data = fetch_account_data()
category_info = get_category_metadata()
temporary_rate_limit_delay = calculate_backoff_delay()
categorization_result = process_account_categorization()
confidence_value = compute_confidence_score()
selected_account = get_selected_account()
```

---

## 🎨 Code Formatting

### String Quotes

- Use **double quotes `"`** for regular strings
- Use **single quotes `'`** for dict keys and f-string embedded quotes

```python
# ✅ CORRECT
name = "John Doe"
message = "Hello, world!"
data = {"user_id": "123", "name": f"Hello {name}"}

# ❌ INCORRECT
name = 'John Doe'
message = 'Hello, world!'
data = {'user_id': '123', 'name': f'Hello {name}'}
```

### Indentation

- **4 spaces** per indentation level
- ❌ **NEVER** use tabs
- Configure your editor to convert tabs to 4 spaces

### Blank Lines

```python
# Two blank lines before class definitions
import os


class MyClass:
    pass


class AnotherClass:
    pass


# Two blank lines before top-level functions
def top_level_function():
    pass


def another_top_level():
    pass


# One blank line between methods
class MyClass:
    def method_one(self):
        pass

    def method_two(self):
        pass
```

---

## 📚 Docstrings (Google Style)

### Module Docstring

```python
"""Module for scanning X accounts.

This module provides functionality for scanning and analyzing
accounts that a user follows on X (Twitter). It includes
async operations for fetching data and categorizing accounts.
"""
```

### Function/Method Docstring

```python
def categorize_account(
    account: Account,
    categories: List[Category],
    confidence_threshold: float = 0.7
) -> CategoryAssignment:
    """Categorize an account using AI analysis.

    Analyzes account profile and activity to assign it to the most
    appropriate category from the discovered categories. Uses Grok
    API for intelligent categorization with confidence scoring.

    Args:
        account: The account to categorize with profile metadata.
        categories: List of discovered categories to choose from.
        confidence_threshold: Minimum confidence score (0-1) required
            for category assignment. Defaults to 0.7.

    Returns:
        CategoryAssignment with category ID, confidence score, and
        reasoning for the assignment.

    Raises:
        CategorizationError: If AI service fails or confidence too low.
        ValueError: If categories list is empty.
        XAPIError: If account data is incomplete.

    Example:
        >>> categories = discover_categories(accounts)
        >>> assignment = categorize_account(account, categories)
        >>> print(f"Category: {assignment.category_id}")
        >>> print(f"Confidence: {assignment.confidence:.2f}")
    """
    pass
```

### Class Docstring

```python
class AccountRepository:
    """Repository for managing account data persistence.

    Provides CRUD operations for Account entities with caching
    and batch operations support. Uses SQLAlchemy for ORM.

    Attributes:
        _db: Database manager instance.
        _cache: In-memory cache for frequently accessed accounts.

    Example:
        >>> repo = AccountRepository(db_manager)
        >>> account = repo.get_by_username("elonmusk")
        >>> repo.save(account)
    """

    def __init__(self, db_manager: DatabaseManager):
        """Initialize repository with database manager.

        Args:
            db_manager: Configured database manager instance.
        """
        self._db = db_manager
        self._cache = {}
```

---

## ✅ Code Review Checklist

Before submitting code, verify:

### Readability
- [ ] All variable/function names are extremely self-explanatory
- [ ] No abbreviations used
- [ ] No single-letter variables (except i, j, k, e)
- [ ] Comments only where absolutely necessary
- [ ] Code reads like prose

### DRY
- [ ] No duplicated logic
- [ ] Repeated code extracted into functions
- [ ] No copy-paste code

### Size Limits
- [ ] All files ≤ 800 lines (ideally ≤ 500)
- [ ] All functions ≤ 100 lines (ideally ≤ 60)
- [ ] Cyclomatic complexity ≤ 15 (ideally ≤ 10)

### PEP 8
- [ ] All imports at top of file
- [ ] Imports properly ordered (stdlib, 3rd-party, local)
- [ ] Line length ≤ 88 characters
- [ ] Proper spacing and indentation
- [ ] Double quotes for strings

### Quality
- [ ] Type hints on all function signatures
- [ ] Docstrings for all public functions/classes
- [ ] Guard clauses instead of deep nesting
- [ ] Early returns to reduce complexity
- [ ] Specific exception handling (no bare `except`)

### Tests
- [ ] Unit tests for new functions
- [ ] Edge cases covered
- [ ] Error cases tested

---

**Last Updated**: 2025-01-20
**Maintained By**: Development Team
