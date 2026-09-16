# Repository contribution rules

These rules exist to keep the codebase readable, understandable, secure, and
easy for other developers to reuse. Prefer the simplest correct solution and
follow established patterns before introducing a new one.

## Rule precedence

When rules conflict, apply them in this order:

1. Correctness, security, privacy, and accessibility.
2. Framework, language, and repository conventions.
3. Readability, maintainability, and consistency.
4. Performance, when supported by measurements or a clear operational need.
5. Personal style preferences.

Rules specific to a directory or technology may refine these general rules.
Document a deliberate exception when it affects future maintainers.

## Language and naming

Code, documentation, identifiers, commit messages, and user-facing technical
text must be written in English unless a product requirement says otherwise.

### Python

- Use `snake_case` for functions, methods, variables, properties, fields, and
  related names.
- Use `PascalCase` for classes, managers, querysets, and exceptions.
- Use `UPPER_SNAKE_CASE` for module constants and environment variables.
- Prefix private implementation details with `_`.
- Use descriptive boolean names such as `is_...`, `has_...`, and `can_...`.

### TypeScript and React

- Use `camelCase` for variables, functions, helpers, and local hook values.
- Use `PascalCase` for components, types, interfaces, and exported type-like
  constructs.
- Use a leading underscore only for intentionally ignored values.
- Prefer descriptive names over abbreviations. Use established domain
  abbreviations consistently when they improve clarity.

### CSS and styling

- Follow the existing styling system and naming convention.
- Use descriptive, namespaced BEM-like classes where that is the project
  convention, for example `c__button--medium`.
- Keep design tokens hierarchical and scoped to their domain, for example
  `--c--components--...`, `--c--globals--...`, or `--bn-...`.

### Shell, Make, CI, and data schemas

- Use `UPPER_SNAKE_CASE` for shell, Make, and workflow environment variables.
- Use `kebab-case` for Make targets, workflow job IDs, and workflow steps.
- Use lowercase `snake_case` for database tables, constraints, and identifiers.
- Prefer descriptive file names and keep related documentation names aligned
  with the feature they describe.

Favor consistency with neighboring code. Do not rename unrelated code merely to
apply a preferred convention.

## Readability and design

- Give each function, class, and module one clear responsibility.
- Keep public APIs explicit: declare input and output types and document
  constraints, side effects, and failure modes.
- Prefer guard clauses, shallow nesting, and small composable helpers.
- Isolate side effects such as I/O, network calls, filesystem access, and
  database writes.
- Replace unexplained magic numbers and strings with named constants.
- Remove dead code, unreachable branches, unused imports, and commented-out
  legacy implementations.
- Reuse existing utilities and components instead of duplicating behavior.
- Preserve useful comments and update comments and documentation when behavior
  changes. Use the comment syntax required by the language (`#`, `//`, `/* */`,
  or the equivalent), with `TODO:`, `FIXME:`, and `NOTE:` prefixes.

### Function and method docstrings

- Public functions and methods must have a docstring that explains their
  purpose, inputs, outputs, constraints, side effects, and raised exceptions
  when relevant.
- Private functions and methods must have a docstring when their behavior,
  invariants, resource management, or side effects are not obvious from their
  name and implementation.
- A trivial private helper does not need a docstring when its name, signature,
  and implementation clearly explain what it does.
- Keep docstrings next to the function or method they describe, and update them
  whenever the behavior or contract changes.
- Use the documentation format established by the language and framework. For
  example, use Python docstrings for Python functions and TSDoc comments for
  exported TypeScript functions when the project uses TSDoc.

### Practical size guidance

There is no universal ideal function or file length. Treat a function longer
than roughly 25 lines of logic or a file approaching 600 lines as a prompt to
review its responsibilities and consider extraction, not as an automatic
violation. Do not split code artificially when doing so would make the design
harder to follow.

## Error handling and contracts

- Validate all external input, including user input, API responses, URL
  parameters, files, and environment variables.
- Define clear contracts between modules: inputs, outputs, invariants, and
  failure modes.
- Fail fast with actionable errors when an invariant is violated.
- Never leave `catch` or exception handlers empty. Log safely, recover, or
  re-raise with useful context.
- Handle asynchronous failures explicitly and clean up resources such as file
  handles, connections, subscriptions, and event listeners.
- Do not expose stack traces, credentials, tokens, or personal data in user
  responses or logs.

## Security and privacy

- Never hardcode secrets, API keys, credentials, or private certificates.
- Never commit real secrets or `.env` files. Document required variables in an
  appropriate example file without including secret values.
- Validate and sanitize input before database operations, filesystem access,
  template rendering, or command execution.
- Use parameterized database queries; never build queries by concatenating
  untrusted input.
- Apply authentication and authorization at the server boundary, not only in
  the client.
- Use secure defaults for cookies, headers, CORS, file uploads, and network
  timeouts according to the technology in use.
- Avoid logging sensitive data and review security-sensitive changes carefully.

## Testing

Tests must be readable, deterministic, isolated, and named after the behavior
they verify. Happy-path coverage alone is insufficient.

For changed behavior, cover the relevant combination of:

- expected behavior and deterministic output;
- invalid input and meaningful error handling;
- empty, boundary, and unusually large values;
- permission, timeout, and dependency-failure cases;
- integration behavior when module boundaries or external systems are involved.

Every public behavior and regression should have automated coverage. A trivial
private helper does not require a separate test when it is fully exercised by a
higher-level test. Add tests for every meaningful branch, or explain why a
branch is unreachable or safely covered indirectly.

## Frontend accessibility and user experience

- Use semantic HTML and accessible names for interactive controls.
- Ensure keyboard navigation, visible focus, appropriate contrast, and useful
  validation and error messages.
- Support loading, success, empty, and failure states for data-driven views.
- Clean up subscriptions, timers, listeners, and other resources.
- Verify responsive behavior at supported viewport sizes and avoid relying only
  on color to communicate meaning.
- Follow the repository's localization and formatting conventions for user-facing
  text.

## Documentation

Update documentation when adding or changing:

- public APIs, commands, configuration, or environment variables;
- user-facing behavior or supported workflows;
- architecture, integration points, or operational procedures;
- breaking changes, migrations, deprecations, or security-sensitive behavior.

Examples must match the current implementation and should be tested when
practical. Prefer linking to a single authoritative document rather than
duplicating instructions in several places.

## Verification gate

Before declaring work complete, run the repository's documented formatting,
linting, type-checking, build, and test commands. If a command is not available,
state that explicitly and run the closest applicable check. Completion requires:

1. no new formatter, linter, or type-checker errors;
2. existing tests passing;
3. new or changed behavior covered by regression tests;
4. generated files, migrations, and documentation updated where applicable;
5. the final diff reviewed for accidental changes, secrets, and dead code.

Do not claim that checks passed without running them. Existing unrelated failures
must be reported with their command and error summary.

## Agent directives: open-source contribution

### Code standards and architecture

- Follow the architectural patterns present in the immediate file context.
- Use explicit typing for all public function signatures and return types.
- Ensure all introduced branches (if/else, exceptions) are covered by automated tests.
- All code and documentation must be in English.

### Pull request format

- Title: Follow Conventional Commits format.
- Body: Include:
  - Motivation: Issue fixed.
  - Changes: Bullet points of exact additions.
  - Verification: Commands run and output summary.
  - Disclosure: "Generated with assistance of [Agent/Model Name]."
