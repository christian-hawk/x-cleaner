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


### Self-Documenting Code

- ✅ Variable and function names must be **EXTREMELY self-explanatory**
- ✅ Anyone reading the code should understand it **WITHOUT comments**
- ❌ Avoid abbreviations: `usr` → `user`, `acc` → `account`, `cat` → `category`
- ❌ Avoid single letters except for: `i`, `j`, `k` (loops), `e` (exceptions)


### Comments (A Necessary Evil)

- ⚠️ **Comments are a code smell** - they indicate the code isn't clear enough
- ✅ Use comments ONLY for:
  - Complex algorithms that can't be simplified
  - Business logic WHY (not WHAT or HOW)
  - Workarounds for external API quirks
  - Performance optimization explanations
- ❌ **NEVER** comment obvious code
- ❌ **NEVER** use comments to explain bad variable names → rename instead


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


---

## 📝 PEP 8 Style Guide

**Base Standard**: **PEP 8** (MANDATORY - no exceptions without justification)

### Line Length

- **Maximum**: 88 characters (Black formatter default)
- Break long lines using parentheses or backslashes
- Prefer breaking after operators


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


### Whitespace


---

## 🏷️ Naming Conventions (MANDATORY)

**Golden Rule**: Names must be so clear that comments become unnecessary.

### Classes: PascalCase

Nouns describing what the class represents.


### Functions/Methods: snake_case

Verbs describing what they do.


### Variables: snake_case

EXTREMELY descriptive - explain exactly what the variable contains.


### Constants: UPPER_SNAKE_CASE

Describe the value's purpose and context.


### Boolean Variables

Start with `is_`, `has_`, `should_`, `can_`, `will_`


### Private Members: Leading Underscore


### Type Aliases: PascalCase

Describe the type's semantic meaning.


---

## 🚫 Naming Anti-Patterns (FORBIDDEN)

### Single Letter Variables

❌ **FORBIDDEN** except for:
- `i`, `j`, `k` in simple loops
- `e` for exceptions
- `_` for intentionally unused values


### Abbreviations

❌ **COMPLETELY FORBIDDEN**


### Numbers in Names

❌ **FORBIDDEN** (except when semantically meaningful)


### Vague Names

❌ **FORBIDDEN**


---

## 🎨 Code Formatting

### String Quotes

- Use **double quotes `"`** for regular strings
- Use **single quotes `'`** for dict keys and f-string embedded quotes


### Indentation

- **4 spaces** per indentation level
- ❌ **NEVER** use tabs
- Configure your editor to convert tabs to 4 spaces

### Blank Lines


---

## 📚 Docstrings (Google Style)

### Module Docstring


### Function/Method Docstring


### Class Docstring


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
