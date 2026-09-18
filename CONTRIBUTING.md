# Contributing to Bienvenue à La Suite

First off, thank you for considering contributing to **Bienvenue à La Suite**! We welcome contributions from public service agents, open-source developers, and digital accessibility enthusiasts.

This project is part of the [La Suite Numérique](https://lasuite.numerique.gouv.fr) ecosystem and is licensed under the [MIT License](LICENSE).

---

## Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.

---

## Development Workflow

### 1. Fork & Branch

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone git@github.com:<your-username>/bienvenue-lasuite.git
   cd bienvenue-lasuite
   ```
3. Create a descriptive topic branch from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   # or
   git checkout -b fix/resolve-issue-123
   ```

Branch naming conventions:
- `feat/`: New feature or user-facing capability.
- `fix/`: Bug fix or patch.
- `docs/`: Documentation updates.
- `chore/`: Tooling, dependency, or configuration updates.
- `refactor/`: Code reorganization without functional changes.

---

### 2. Local Environment Setup

The simplest way to develop is using **Docker Compose** and the root **Makefile**:

```bash
# Copy example environment file
cp .env.example .env

# Start all containers (frontend, backend, keycloak, postgres, grist)
make up

# Apply database migrations
make migrate

# Seed initial demonstration data
make seed
```

Local service URLs:
- **Frontend App**: [http://localhost:3000](http://localhost:3000)
- **Django REST API**: [http://localhost:8000](http://localhost:8000)
- **Keycloak Auth**: [http://localhost:8180](http://localhost:8180) (`admin` / `admin`)
- **Grist Spreadsheet**: [http://localhost:8585](http://localhost:8585)

---

### 3. Coding Standards

- **Language**: All code, docstrings, comments, variable names, and commit messages must be strictly in **English**.
- **Indentation & Formatting**:
  - **Frontend (React / TypeScript)**: Use **tabs** for indentation. Keep files under 600 lines.
  - **Backend (Python / Django)**: Use **4 spaces** following PEP 8. Follow DRF best practices.
- **Accessibility & Design**:
  - Comply with the French state design system (DSFR / *La Suite UI*).
  - Use SVG icons for UI glyphs. Do not introduce raw emoji characters into UI components.
- **Performance**:
  - Avoid N+1 database queries using `select_related` and `prefetch_related`.

---

### 4. Mandatory Testing

Before submitting a Pull Request, you **must** ensure that all tests pass:

```bash
make test
```

This runs:
1. `python manage.py test` (Django test suite, 111+ tests).
2. `npm run build` (`tsc --noEmit && vite build` TypeScript strict check).
3. `docker compose config` (syntax verification).

---

### 5. Commit Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```text
<type>(<scope>): <short description in present tense>

[optional body explaining rationale]
```

Examples:
- `feat(backend): add Service and AgentComment models`
- `fix(frontend): translate checklist UI and step locked alerts to English`
- `docs: add contributing and security guidelines`

---

### 6. Submitting a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feat/my-new-feature
   ```
2. Open a Pull Request against the `main` branch of the official repository.
3. Fill out the PR template completely.
4. Ensure all GitHub Actions CI checks turn green.
5. Address any code review feedback promptly.
