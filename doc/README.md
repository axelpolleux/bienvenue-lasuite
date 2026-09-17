# Technical Documentation Index

Welcome to the comprehensive architecture and implementation documentation for **Bienvenue à La Suite**.

---

## Documentation Suite

| Document                                                              | Description                                                                                                                                                                |
| :-------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[00. System Architecture Overview](00-architecture-overview.md)**   | High-level system architecture, actors, core components, and main user workflows.                                                                                          |
| **[01. Database Schema & Data Model](01-data-model.md)**              | PostgreSQL relational tables, entity-relationship diagram, field specifications, and indexes.                                                                              |
| **[02. Backend BFF & API Specifications](02-backend-bff.md)**         | Django Backend-For-Frontend architecture, REST API endpoints, auth mechanisms, and service layer.                                                                          |
| **[03. Frontend Application Architecture](03-frontend-app.md)**       | React + TypeScript app design, sequential step locking, La Suite UI Kit components (`@gouvfr-lasuite/ui-components`, `@gouvfr-lasuite/ui-tokens`), and RGAA accessibility. |
| **[04. External Integrations Guide](04-external-integrations.md)**    | Grist REST API (manager-triggered pull sync, no webhook), Keycloak OIDC authentication, and La Suite: Fichiers verification.                                               |
| **[05. Local Development & Testing Guide](05-local-development.md)**  | Docker Compose configuration, environment variables, local run commands, and test recipes.                                                                                 |
| **[06. Global Plan Evaluation Report](06-plan-evaluation-report.md)** | Principal Architect scorecard, feasibility analysis, risk matrix, and 7-phase execution roadmap.                                                                           |
| **[REST API Reference](api/README.md)**                              | Concise REST API endpoint reference, authentication methods, payload schemas, and local testing curl recipes.                             |

---
