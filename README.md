# Bienvenue à La Suite

> Modular onboarding companion for [La Suite Numérique](https://lasuite.numerique.gouv.fr) (DINUM), powered by Grist & ProConnect.

![Status: Concept](https://img.shields.io/badge/status-hackathon-blue.svg) ![Accessibility: RGAA](https://img.shields.io/badge/accessibility-RGAA%20AA-blueviolet.svg) ![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg) ![Grist](https://img.shields.io/badge/templates-Grist-orange.svg)

## Overview

**Bienvenue à La Suite** is an accessible onboarding platform for French civil servants. It streamlines newcomer arrival with an interactive, keyboard-friendly checklist (Fichiers drive verification, Tchap messaging, official email signature), while giving managers real-time supervision and customizable Grist templates.

## Quick Start (Docker & Makefile)

```bash
make up     # Start all 5 containers (frontend :3000, backend :8000, keycloak :8180, db :25432, grist :8585)
make test   # Run full test suite (111 tests) and frontend build
make reset  # Reset checklist tasks and signature status to 0%
make down   # Stop all running containers
```

Local access: **Frontend** at [localhost:3000](http://localhost:3000) · **API** at [localhost:8000](http://localhost:8000) · **Keycloak** at [localhost:8180](http://localhost:8180) (`agent@bienvenue.local` / `agent`).

## Development & Contribution Workflow

To maintain code quality and stability, all contributors must follow this standard branch-and-test workflow:

### 1. Create a Dedicated Branch

Never commit directly to `main` or production branches. Create a new branch with a clear prefix:

```bash
git checkout -b feat/your-feature-name
# or for bug fixes:
git checkout -b fix/your-bugfix-name
```

### 2. Start Local Environment

Ensure all containers are running and database migrations are up to date:

```bash
make up        # Starts PostgreSQL, Keycloak, Grist, Backend, and Frontend
make migrate   # Applies latest Django database migrations
```

### 3. Coding Guidelines

- **Language**: English for all code, comments, docstrings, and commit messages.
- **Style**: Indentation with tabs for Frontend (React/TypeScript) and 4 spaces for Backend (Python/PEP 8).
- **Constraints**: Keep functions concise (max 60 lines) and files focused (max 600 lines).
- **Zero Raw Emojis**: Never use raw emojis in UI code or comments; use DSFR / Lucide SVG icons.

### 4. Run Mandatory Local Tests

Before pushing or creating a PR, you **must** verify that all tests pass locally:

```bash
make test
```

This command automatically executes:

- Backend test suite: `docker compose exec backend python manage.py test` (all 111 tests must pass).
- Frontend build check: `docker compose exec frontend npm run build` (0 TypeScript or Vite compilation errors).

### 5. Commit and Open a Pull Request

Commit your changes using atomic commits following Conventional Commits format:

```bash
git add <files>
git commit -m "feat(scope): concise description of changes"
git push -u origin feat/your-feature-name
```

Open a Pull Request on GitHub. GitHub Actions CI (`.github/workflows/ci.yml`) will automatically run the automated test suite and frontend build. All checks must pass before merging.

## Technical Documentation

Comprehensive specifications are in [`doc/`](doc/README.md):

- [System Architecture](doc/00-architecture-overview.md) · [Data Model](doc/01-data-model.md) · [Backend BFF](doc/02-backend-bff.md)
- [Frontend Architecture](doc/03-frontend-app.md) · [External Integrations](doc/04-external-integrations.md) · [REST API Specs](doc/api/README.md)

## Team Members

- **Axel Polleux** ([@axelpolleux](https://github.com/axelpolleux))
- **Diego Luna** ([@Diego-Luna](https://github.com/Diego-Luna))
- **Julie Bellec** ([@jubellec](https://github.com/jubellec))
- **Benjamin Karas** ([@komorebi-32](https://github.com/komorebi-32))
- **Melanie Demaret** ([@AlrightMela](https://github.com/AlrightMela))

## Configuration

Pre-configured out of the box with Docker. To customize: `cp .env.example .env`.
