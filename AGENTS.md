# Global Rules

Goal: Is neseary to majke de code readable, easly to read, and maintaintable, so we only will include the most important information in the code. For the comunity of Open Source.

## Code Quality Standards

### Size Limits

- **Functions**: Maximum **25 lines** of logic. Split larger functions into smaller, well-named helpers.
- **Files**: Maximum **4 functions** per file. Split into separate modules when approaching this limit.

### Error Handling

- NEVER leave `catch` blocks empty. Always log or rethrow.
- Handle all async errors (unhandled promise rejections, missing try/catch on await).
- Validate all external inputs (user input, API responses, URL params).

### Security

- Never hardcode secrets, API keys, or credentials in source code.
- Always validate and sanitize user inputs before database operations.
- Use parameterized queries never string concatenation for SQL/NoSQL.

### Documentation

- Add JSDoc/docstrings to all public functions and complex logic.
- Preserve ALL existing comments and docstrings unrelated to your changes.
- Use the comment format: `// !` (alerts), `// ?` (queries), `// TODO:` (pending), `// *` (highlights).

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

### Pull Request Format

- Title: Follow Conventional Commits format.
- Body: Include:
  - Motivation: Issue fixed.
  - Changes: Bullet points of exact additions.
  - Verification: Commands run and output summary.
  - Disclosure: "Generated with assistance of [Agent/Model Name]."
