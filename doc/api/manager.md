# Manager Dashboard Endpoints

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

Management endpoints allowing team leads and administrators to track newcomer onboarding progress and reassign templates.

## Authorization & Roles

All endpoints in this section require the **`manager`** role (`Agent.role = RoleChoices.MANAGER`), enforced via DRF's `IsManager` permission class:

| Role Tested | Access Granted | Rejected Status |
| :--- | :--- | :--- |
| **`manager`** | Yes | — |
| **`new_agent`** | No | `403 Forbidden` (`{"detail": "You do not have permission to perform this action."}`) |
| **Unauthenticated** | No | `401 Unauthorized` (`{"detail": "Authentication credentials were not provided."}`) |

---

## Endpoints Summary

| Method | Path | Role | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/manager/overview/` | `manager` | [Overview of all newcomers with progress % and active step](#1-get-apimanageroverview) |
| `PATCH` | `/api/agents/{id}/assign-template/` | `manager` | [Reassign an onboarding template to an agent](#2-patch-apiagentsidassign-template) |

---

## 1. GET /api/manager/overview/

Returns an aggregated list of newcomers (`role = "new_agent"`), their assigned template name, progress percentage, email signature status, and current active step. Results are ordered newest first (`-created_at`).

- **Role**: `manager` (see [Authentication](authentication.md))

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Authenticated as manager | Total newcomer count and agent summary array (see below) |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`403 Forbidden`** | Authenticated user is not a manager | `{"detail": "You do not have permission to perform this action."}` |

### Response Example (`200 OK`)

```json
{
  "total_newcomers": 2,
  "agents": [
    {
      "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "name": "Alex Martin",
      "email": "alex.martin@gouv.fr",
      "template_name": "Socle Commun Administration",
      "progress_percentage": 33,
      "signature_accepted": false,
      "current_step": "Se connecter à Tchap",
      "created_at": "2026-09-16T08:00:00Z"
    },
    {
      "id": "5b2d8e41-1122-3344-5566-778899aabbcc",
      "name": "Sarah Connor",
      "email": "sarah.connor@gouv.fr",
      "template_name": "Template Sécurité",
      "progress_percentage": 100,
      "signature_accepted": true,
      "current_step": "All tasks completed",
      "created_at": "2026-09-15T09:30:00Z"
    }
  ]
}
```

### Curl Example (Local Dev)

```bash
curl -X GET "http://localhost:8000/api/manager/overview/" \
  -H "X-Dev-User-Email: manager.boss@gouv.fr" \
  -H "Accept: application/json"
```

---

## 2. PATCH /api/agents/{id}/assign-template/

Reassigns an onboarding template to a specific agent.

- **Role**: `manager` (see [Authentication](authentication.md))

### Parameters

| Parameter | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | Path | UUID | Yes | Target `Agent` identifier. |
| `template_id` | Body | UUID | Yes | UUID of the `Template` to assign. |

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Template reassigned | `{"agent_id": "<uuid>", "template_id": "<uuid>", "template_name": "...", "message": "Template assigned successfully."}` |
| **`400 Bad Request`** | Missing or empty `template_id` | `{"error": "template_id is required."}` |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`403 Forbidden`** | Authenticated user is not a manager | `{"detail": "You do not have permission to perform this action."}` |
| **`404 Not Found`** | Agent or Template UUID not found | `{"error": "Template not found."}` or `{"detail": "Not found."}` |

### Response Example (`200 OK`)

```json
{
  "agent_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "template_id": "e3b0c442-98fc-1c14-9af0-2a8b5f700001",
  "template_name": "Socle Commun Administration",
  "message": "Template assigned successfully."
}
```

### Curl Example (Local Dev)

```bash
curl -X PATCH "http://localhost:8000/api/agents/7c9e6679-7425-40de-944b-e07fc1f90ae7/assign-template/" \
  -H "X-Dev-User-Email: manager.boss@gouv.fr" \
  -H "Content-Type: application/json" \
  -d '{"template_id": "e3b0c442-98fc-1c14-9af0-2a8b5f700001"}'
```

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
