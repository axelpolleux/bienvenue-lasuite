# Global Rules

Goal: Is neseary to majke de code readable, easly to read, and maintaintable, so we only will include the most important information in the code. For the comunity of Open Source.

## Naming conventions

This repository uses different naming conventions depending on the layer, language, and file type.

### Backend Python

- Use `snake_case` for:
  - functions
  - methods
  - variables
  - properties
  - model field names
  - related names
- Use `PascalCase` for:
  - classes
  - managers
  - querysets
  - exceptions
- Use `UPPER_SNAKE_CASE` for:
  - module-level constants
  - Django settings-like constants
  - environment variable names
- Use a leading underscore for:
  - private/internal attributes
  - cached implementation details
- Use standard Python dunder names for protocol methods:
  - `__str__`
  - `__init__`
  - etc.
- Prefer boolean names beginning with:
  - `is_...`
  - `has_...`
  - `can_...`

### Frontend TypeScript / React

- Use `camelCase` for:
  - variables
  - functions
  - helpers
  - hooks-local values
- Use `PascalCase` for:
  - React components
  - type aliases
  - interfaces
  - exported type-like constructs
- Use a leading underscore for:
  - throwaway / ignored values when needed
- Prefer descriptive function names rather than abbreviated ones.

### CSS / styling

- Use namespaced, BEM-like class names:
  - `c__button`
  - `c__modal__backdrop`
  - `c__button--medium`
- Use hierarchical custom-property names for design tokens:
  - `--c--components--...`
  - `--c--globals--...`
  - `--bn-...`
  - `--mantine-...`
- Keep class names and token names descriptive and structured by domain/component/state.

### Makefile and shell

- Use `UPPER_SNAKE_CASE` for Make variables and shell environment variables.
- Use `kebab-case` for Make targets.
- Prefer descriptive target names like:
  - `run-backend`
  - `frontend-i18n-compile`
  - `generate-secret-keys`
- Keep helper variables grouped in the VARIABLES section.
- Keep rules grouped and alphabetically sorted where practical.

### GitHub Actions

- Use descriptive `kebab-case` job IDs and workflow steps.
- Use `UPPER_SNAKE_CASE` for workflow environment variables.
- Use clear reusable workflow input names, often in `kebab-case`.

### Documentation and filenames

- Prefer descriptive file names.
- Use `kebab-case` for Markdown documentation files where appropriate.
- Keep section and file names aligned with the feature or topic they describe.

### Database / schema names

- Use lowercase with underscores for:
  - table names
  - constraint names
  - database identifiers
- Keep related names consistent with model and relation names.

### General guidance

- Favor consistency with neighboring files over inventing new patterns.
- Match the existing convention of the file you are editing.
- Use names that make the role of the value obvious without extra context.
- Avoid ambiguous abbreviations unless they are already established in the codebase.

## Code Quality Standards

### Language

- Every variable, function, class and module names must be in English

### Function Design and Responsibility

- Every function must have exactly one responsibility.
- A function must do one clearly defined job and do it well.
- If a function starts handling parsing, validation, transformation, and output formatting together, split it into helpers.
- Prefer composition of small functions over nested, monolithic logic.
- Keep functions short and readable. Target concise functions; extract helpers as soon as branching or nesting grows.

### Mandatory Docstrings

- Every function must include a docstring.
- The docstring must explicitly describe:
  - what the function does
  - its inputs (name, type/shape, constraints)
  - its output (type/shape and meaning)
  - raised exceptions or failure modes (when relevant)
- Docstrings must be written and updated together with code changes. No stale documentation.
- Preserve ALL existing comments and docstrings unrelated to your changes.
- Use the comment format: `// !` (alerts), `// ?` (queries), `// TODO:` (pending), `// *` (highlights).

### Clean Code Rules

- Use meaningful and unambiguous names for variables, functions, classes, and modules.
- Eliminate magic numbers by defining named constants with clear intent.
- Remove dead code immediately (unused variables, unreachable branches, commented-out legacy blocks).
- Prefer explicitness over cleverness; optimize for maintainability.
- Keep side effects isolated and obvious (I/O, network, filesystem, DB writes).
- Avoid deep nesting. Use guard clauses and helper extraction.
- Do not duplicate logic. Reuse shared helpers for repeated behavior.

### Size Limits

- **Functions**: Maximum **25 lines** of logic. Split larger functions into smaller, well-named helpers.
- **Files**: Maximum **4 functions** per file. Split into separate modules when approaching this limit.

### Error Handling

- NEVER leave `catch` blocks empty. Always log or rethrow.
- Handle all async errors (unhandled promise rejections, missing try/catch on await).
- Validate all external inputs (user input, API responses, URL params).
- Fail fast with clear, actionable error messages.
- Define and respect clear contracts between modules (inputs, outputs, invariants).

### Security

- Never hardcode secrets, API keys, or credentials in source code.
- Always validate and sanitize user inputs before database operations.
- Use parameterized queries never string concatenation for SQL/NoSQL.

### funtions

- is important to maneg the funcoin very explicited in the names of the functions. so we can undestand what the function does
- the names of the functions must be very explicited and easy to understand
- the names of the functions must be in english.
- simple name of varibles.

## Agent Directives: Open Source Contribution

### Code Standards & Architecture

- Follow the architectural patterns present in the immediate file context.
- Use explicit typing for all public function signatures and return types.
- Ensure all introduced branches (if/else, exceptions) are covered by automated tests.
- All the code and documentation is must be in english.

### Verification Gate

Before signaling completion, you must execute and verify:

1. Linters: Zero errors, zero warnings.
2. Type checkers: Strict pass.
3. Test suite: Existing tests pass; new regression/unit tests pass.

### Testing Requirements (Mandatory)

- Unit tests are required for all functions.
- "Happy path only" tests are not sufficient.
- For each function, tests must cover at least:
  - expected behavior
  - invalid input handling
  - edge conditions
  - deterministic output expectations
- Tests must be readable, deterministic, and isolated.
- Keep test names descriptive: they should state behavior and expected result.

### Pull Request Format

- Title: Follow Conventional Commits format.
- Body: Include:
  - Motivation: Issue fixed.
  - Changes: Bullet points of exact additions.
  - Verification: Commands run and output summary.
  - Disclosure: "Generated with assistance of [Agent/Model Name]."
