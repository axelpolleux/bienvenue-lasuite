# Agent Onboarding & Signature Endpoints

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

Endpoints for retrieving the agent onboarding bundle and validating institutional email signatures.

## Endpoints Summary

| Method | Path | Role | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/onboarding/me/` | `new_agent`, `manager` | [Retrieve complete onboarding bundle, checklist, and resources](#1-get-apionboardingme) |
| `POST` | `/api/signature/accept/` | `new_agent`, `manager` | [Validate institutional email signature acceptance](#2-post-apisignatureaccept) |

---

## 1. GET /api/onboarding/me/

Retrieves the authenticated agent's profile, onboarding progress, assigned template, sequential checklist items with lock states, colleagues, documents, and training resources.

- **Role**: `new_agent` or `manager` (see [Authentication](authentication.md))

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Profile found | Complete onboarding bundle (see below) |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`404 Not Found`** | Missing agent profile | `{"error": "Agent profile not found."}` |

### Response Example (`200 OK`)

```json
{
  "agent": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "email": "alex.martin@gouv.fr",
    "name": "Alex Martin",
    "role": "new_agent",
    "signature_accepted": false,
    "created_at": "2026-09-16T08:00:00Z",
    "progress": {
      "total_tasks": 3,
      "completed_tasks": 1,
      "percentage": 33
    }
  },
  "template": {
    "id": "e3b0c442-98fc-1c14-9af0-2a8b5f700001",
    "name": "Socle Commun Administration",
    "email_signature": "Alex Martin — Direction du Numérique"
  },
  "todos": [
    {
      "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
      "order": 1,
      "label": "Activer mon espace Fichiers",
      "service_link": "https://fichiers.numerique.gouv.fr",
      "validation_type": "API_CHECK",
      "done": true,
      "done_at": "2026-09-16T08:30:00Z",
      "is_locked": false
    },
    {
      "id": "b8a5d3f2-1234-5678-9abc-def012345678",
      "order": 2,
      "label": "Se connecter à Tchap",
      "service_link": "https://tchap.gouv.fr",
      "validation_type": "MANUAL",
      "done": false,
      "done_at": null,
      "is_locked": false
    }
  ],
  "colleagues": [
    { "id": "1a2b3c4d-5678-90ab-cdef-1234567890ab", "name": "Camille Dupont (Référent IT)", "tchap_link": "https://tchap.gouv.fr/#/user/@camille.dupont:agent.gouv.fr" }
  ],
  "documents": [
    { "id": "2b3c4d5e-6789-01ab-cdef-2345678901bc", "title": "Charte Informatique et Sécurité", "url": "https://fichiers.numerique.gouv.fr/s/charte", "format": "pdf" }
  ],
  "trainings": [
    { "id": "3c4d5e6f-7890-12ab-cdef-3456789012cd", "title": "Prise en main de La Suite Numérique", "video_url": "https://tube.numerique.gouv.fr/w/example", "duration_minutes": 15 }
  ]
}
```

### Curl Example (Local Dev)

```bash
curl -X GET "http://localhost:8000/api/onboarding/me/" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" \
  -H "Accept: application/json"
```

---

## 2. POST /api/signature/accept/

Marks the official email signature as accepted for the authenticated agent (`signature_accepted = true`).

- **Role**: `new_agent` or `manager` (see [Authentication](authentication.md))

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Signature validated | `{"signature_accepted": true, "message": "Signature validated successfully."}` |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`404 Not Found`** | Missing agent profile | `{"error": "Agent profile not found."}` |

### Response Example (`200 OK`)

```json
{
  "signature_accepted": true,
  "message": "Signature validated successfully."
}
```

### Curl Example (Local Dev)

```bash
curl -X POST "http://localhost:8000/api/signature/accept/" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" \
  -H "Accept: application/json"
```

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
