# Bienvenue à La Suite — REST API Reference

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

REST API reference for **Bienvenue à La Suite** (`/api/`), powered by a Django REST Framework (DRF) Backend-For-Frontend (BFF) for civil servant onboarding within the French public administration.

- **Base URL (Local)**: `http://localhost:8000/api`
- **Default Format**: JSON (`Content-Type: application/json`, `Accept: application/json`)
- **Authentication**: Handled via `X-Dev-User-Email` in development (`DEBUG=True`) and Keycloak OIDC JWT in production. See [Authentication & Permissions](authentication.md).

---

## Documentation Sections

| Section                                                 | Description                                                                             | Key Endpoints / Topics                                                    |
| :------------------------------------------------------ | :-------------------------------------------------------------------------------------- | :------------------------------------------------------------------------ |
| **[`Authentication & Permissions`](authentication.md)** | Auth strategy, dev headers, Keycloak JWT, roles, and security policies.                 | `X-Dev-User-Email`, Keycloak JWT, `IsManager`                             |
| **[`Agent Onboarding & Signature`](onboarding.md)**     | Onboarding bundle, progress calculation, and official email signature.                  | `GET /api/onboarding/me/`<br>`POST /api/signature/accept/`                |
| **[`Todos & Checklist Tasks`](todos.md)**               | Sequential task verification, manual toggle, step locking, and anti-IDOR isolation.     | `POST /api/todos/{id}/verify/`<br>`POST /api/todos/{id}/toggle/`          |
| **[`Manager Dashboard`](manager.md)**                   | Overview of newcomers, completion percentages, active steps, and template assignment.   | `GET /api/manager/overview/`<br>`PATCH /api/agents/{id}/assign-template/` |
| **[`Local Mock Suite`](mock-suite.md)**                 | Local development mocks simulating external La Suite tools (e.g. Fichiers / Nextcloud). | `GET /api/mock-suite/fichiers/users/{email}/`                             |

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
