# Backend BFF & API Specifications

This document defines the architecture, endpoints, and internal services of the Django Backend-For-Frontend (BFF) located in `backend/`.

---

## 1. Directory Structure

The Django application is structured inside `backend/src/` with an `onboarding` app isolating all domain logic:

```text
backend/
├── manage.py
├── pyproject.toml
├── Dockerfile
├── src/
│   ├── settings.py            # DRF, CORS, DB, and OIDC config
│   ├── urls.py                # Main router mounting /api/
│   ├── asgi.py
│   ├── wsgi.py
│   └── onboarding/            # Core domain app
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py          # 7 Models (Agent, Template, TodoItem, etc.)
│       ├── serializers.py     # DRF Serializers for nested responses
│       ├── views/
│       │   ├── __init__.py
│       │   ├── onboarding.py  # Agent endpoints (me, verify, toggle, signature)
│       │   ├── manager.py     # Manager overview, assignment & sync-grist endpoints
│       │   └── mock_suite.py  # Local testing mock for Fichiers service
│       ├── management/commands/
│       │   ├── sync_grist.py                # CLI equivalent of POST /api/manager/sync-grist/
│       │   └── mirror_grist_to_selfhosted.py # Snapshot the cloud doc into our self-hosted one
│       ├── services/
│       │   ├── __init__.py
│       │   ├── grist_client.py # Thin Grist REST API wrapper (list/create/update/delete)
│       │   ├── grist_sync.py   # Upserts Postgres from Grist records, table by table
│       │   └── suite_verifier.py # HTTP client verifying user existence in Fichiers
│       ├── authentication.py  # Keycloak JWT validator & Dev Auth bypass
│       └── urls.py            # /api/ routes
```

---

## 2. Authentication & Identity Strategy

Following the architecture diagram, identity is driven by **Keycloak**, using the agent's institutional `email` as the primary key.

### Development Mode (`DEBUG = True`)
To allow rapid local testing without requiring a live Keycloak server:
- If `DEBUG = True`, the custom authenticator checks the HTTP request header `X-Dev-User-Email`.
- If present, it resolves or creates the corresponding `Agent` record and authenticates the request.
- If absent, it falls back to a default demo agent (`new_agent`).

### Production Mode (`DEBUG = False`)
- The authenticator validates the incoming `Authorization: Bearer <JWT>` against Keycloak's JSON Web Key Set (JWKS).
- Extracts institutional `email`, `name`, and user roles (`manager`, `new_agent`).
- **Security Invariant**: When `DEBUG = False`, the `X-Dev-User-Email` header is **strictly rejected and ignored**. All requests must present a valid, unexpired Keycloak JWT; any unauthorized request receives `401 Unauthorized`.

---

## 3. REST API Endpoints

### 3.1 New Agent Endpoints

#### `GET /api/onboarding/me/`
Retrieves the logged-in agent profile, their assigned template, sequential tasks, colleagues, documents, and trainings.

**Response `200 OK`:**
```json
{
  "agent": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "email": "alex.martin@gouv.fr",
    "name": "Alex Martin",
    "role": "new_agent",
    "signature_accepted": false,
    "progress": {
      "total_tasks": 5,
      "completed_tasks": 1,
      "percentage": 20
    }
  },
  "template": {
    "id": "e3b0c442-98fc-1c14-9af0-2a8b5f700001",
    "name": "Socle Commun Administration",
    "email_signature": "Alex Martin — Direction du Numérique\nMinistère..."
  },
  "todos": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "order": 1,
      "label": "Activer et vérifier mon espace de stockage Fichiers",
      "service_link": "https://fichiers.numerique.gouv.fr",
      "validation_type": "API_CHECK",
      "done": true,
      "done_at": "2026-09-16T08:30:00Z",
      "is_locked": false
    },
    {
      "id": "b8a5d3f2-1234-5678-9abc-def012345678",
      "order": 2,
      "label": "Se connecter à la messagerie Tchap et rejoindre le salon général",
      "service_link": "https://tchap.gouv.fr",
      "validation_type": "MANUAL",
      "done": false,
      "done_at": null,
      "is_locked": false
    }
  ],
  "colleagues": [
    {
      "name": "Camille Dupont (Référent IT)",
      "tchap_link": "https://tchap.gouv.fr/#/user/@camille.dupont:agent.gouv.fr"
    }
  ],
  "documents": [
    {
      "title": "Charte Informatique et Sécurité",
      "url": "https://fichiers.numerique.gouv.fr/s/charte",
      "format": "pdf"
    }
  ],
  "trainings": [
    {
      "title": "Prise en main de La Suite Numérique",
      "video_url": "https://tube.numerique.gouv.fr/w/example",
      "duration_minutes": 15
    }
  ]
}
```

---

#### `POST /api/todos/{id}/verify/`
Executes automated service verification for `API_CHECK` steps (specifically **Fichiers**). `{id}` corresponds to `todo_items.id`.

- **Access Control & Ownership**:
  - The endpoint verifies that the requested `todo_item` belongs to the template assigned to the currently authenticated agent (`agent.assigned_template_id == todo_item.template_id`).
  - Mutates exclusively the `agent_todo_statuses` record scoped to `(agent=request.agent, todo_item=todo_item)`. Unauthorized access or attempts to verify other agents' tasks returns `403 Forbidden`.
- **Logic**:
  1. Verifies that prior sequential tasks are completed (`order < current_task.order`).
  2. URL-encodes and validates `agent.email`, then queries `suite_verifier.check_user_fichiers(agent.email)`.
  3. If service responds with `HTTP 200`, marks `done = true`, records `done_at = now()`.
  4. Unlocks subsequent sequential tasks.

**Response `200 OK` (Verified):**
```json
{
  "todo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "done": true,
  "done_at": "2026-09-16T09:00:00Z",
  "message": "Compte Fichiers validé avec succès."
}
```

**Response `400 Bad Request` (Not yet created in service):**
```json
{
  "todo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "done": false,
  "error": "Utilisateur non trouvé dans le service Fichiers. Veuillez activer votre compte au préalable."
}
```

---

#### `POST /api/todos/{id}/toggle/`
Toggles manual checklist items (`validation_type = "MANUAL"`). `{id}` corresponds to `todo_items.id`.

- **Access Control & Ownership**:
  - Scoped strictly to `request.agent`. Requires task to belong to the agent's assigned template.
  - Rejects toggling if previous sequential items are incomplete (`400 Bad Request`).

**Payload:**
```json
{
  "done": true
}
```

**Response `200 OK`:**
```json
{
  "todo_id": "b8a5d3f2-1234-5678-9abc-def012345678",
  "done": true,
  "done_at": "2026-09-16T09:05:00Z"
}
```

---

#### `POST /api/signature/accept/`
Marks the agent's email signature as configured. Scoped to `request.agent` (`signature_accepted = true`).

**Response `200 OK`:**
```json
{
  "signature_accepted": true,
  "message": "Signature validée."
}
```

---

### 3.2 Manager Endpoints

#### `GET /api/manager/overview/`
Returns a summary of all newcomers, their assigned template, completion percentage, and active step.

**Response `200 OK`:**
```json
{
  "total_newcomers": 3,
  "agents": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "name": "Alex Martin",
      "email": "alex.martin@gouv.fr",
      "template_name": "Socle Commun Administration",
      "progress_percentage": 20,
      "signature_accepted": false,
      "current_step": "Se connecter à Tchap"
    }
  ]
}
```

#### `PATCH /api/agents/{id}/assign-template/`
Assigns or updates the onboarding template for a new agent.

**Payload:**
```json
{
  "template_id": "e3b0c442-98fc-1c14-9af0-2a8b5f700001"
}
```

---

### 3.3 Grist Sync (manager-triggered pull, no webhook)

#### `POST /api/manager/sync-grist/`
Pulls all 6 Grist tables and upserts Postgres. Requires `IsManager`.

- **Security & Authentication**: standard `IsAuthenticated` + `IsManager` — no separate secret, since this is an authenticated app action, not an unauthenticated inbound webhook.
- **Processing Logic**:
  - Invokes `grist_sync.sync_all()`, which calls `sync_table()` per table via the Grist REST API.
  - Performs non-destructive upserts matched on `grist_row_id` for `templates`, `members` (provisions/updates `Agent.assigned_template`), `todo_items`, `colleagues`, `documents`, and `trainings` — `agent_todo_statuses` are never touched, so completion state survives a re-sync.
  - Returns `{"synced": {table: row_count, ...}}`.
- **CLI equivalent**: `python manage.py sync_grist` runs the same `sync_all()` outside the API, useful for local testing or CI.
  - Automatically rolls back the entire transaction if network errors or database constraints fail.

---

### 3.4 Local Testing Mock Service

#### `GET /api/mock-suite/fichiers/users/{email}/`
Simulates La Suite's Fichiers (Nextcloud) user lookup API during local development.
- By default, returns `200 OK` with `{ "exists": true, "email": email }`.
- If query parameter `?status=404` is supplied, returns `404 Not Found` to test the unverified/pending state.
