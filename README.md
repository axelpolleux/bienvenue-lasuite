# Bienvenue à La Suite

> Modular onboarding companion for [La Suite Numérique](https://lasuite.numerique.gouv.fr) (DINUM), powered by Grist & ProConnect.

![Status: Concept](https://img.shields.io/badge/status-hackathon-blue.svg) ![Accessibility: RGAA](https://img.shields.io/badge/accessibility-RGAA%20AA-blueviolet.svg) ![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-336791.svg) ![Grist](https://img.shields.io/badge/templates-Grist-orange.svg)

## Overview
**Bienvenue à La Suite** is an accessible onboarding platform for French civil servants. It streamlines newcomer arrival with an interactive, keyboard-friendly checklist (Fichiers drive verification, Tchap messaging, official email signature), while giving managers real-time supervision and customizable Grist templates.

## Quick Start (Docker & Makefile)
```bash
make up     # Start all 5 containers (frontend :3000, backend :8000, keycloak :8180, db :25432, grist :8585)
make test   # Run full test suite (77 tests) and frontend build
make reset  # Reset checklist tasks and signature status to 0%
make down   # Stop all running containers
```
Local access: **Frontend** at [localhost:3000](http://localhost:3000) · **API** at [localhost:8000](http://localhost:8000) · **Keycloak** at [localhost:8180](http://localhost:8180) (`agent@bienvenue.local` / `agent`).

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
