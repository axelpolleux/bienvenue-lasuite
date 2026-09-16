# Todos & Checklist Tasks Endpoints

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

Endpoints for automated service verification, manual task toggling, sequential step locking rules, and template ownership security.

## Endpoints Summary

| Method | Path | Role | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/todos/{id}/verify/` | `new_agent`, `manager` | [Automated verification against external Fichiers service](#1-post-apitodosidverify) |
| `POST` | `/api/todos/{id}/toggle/` | `new_agent`, `manager` | [Toggle manual checklist item completion state](#2-post-apitodosidtoggle) |

---

## Core Business Rules

### 1. Sequential Step Locking (`is_locked`)

- Each `TodoItem` defines a sequence order (`order: 1, 2, 3...`).
- A task is locked (`is_locked: true`) if **any** prior task in the same template (`order < current.order`) is incomplete (`done: false`).
- The frontend disables interactions on locked tasks until preceding steps are finished.

### 2. Template Ownership Isolation (Anti-IDOR)

- Task interactions are scoped strictly to the authenticated agent's assigned template:
  ```python
  todo = get_object_or_404(TodoItem, id=pk, template=agent.assigned_template)
  ```
- Attempting to verify or toggle a `todo_id` from another template returns `404 Not Found`, preventing IDOR / enumeration attacks.

---

## 1. POST /api/todos/{id}/verify/

Triggers automated external verification against La Suite services (e.g. Fichiers / Nextcloud). On success, marks the task `done = true` and records `done_at`.

- **Role**: `new_agent` or `manager` (see [Authentication](authentication.md))

### Parameters

| Parameter | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | Path | UUID | Yes | Unique identifier of the `TodoItem`. |

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Account verified | `{"todo_id": "<uuid>", "done": true, "done_at": "<iso>", "message": "Account verified successfully."}` |
| **`400 Bad Request`** | Verification failed or unassigned template | `{"todo_id": "<uuid>", "done": false, "error": "User not found in Fichiers service."}` or `{"error": "No assigned template."}` |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`404 Not Found`** | Todo not in agent's template | `{"detail": "No TodoItem matches the given query."}` or `{"error": "Agent profile not found."}` |

### Response Example (`200 OK`)

```json
{
  "todo_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "done": true,
  "done_at": "2026-09-16T08:30:00Z",
  "message": "Account verified successfully."
}
```

### Curl Example (Local Dev)

```bash
curl -X POST "http://localhost:8000/api/todos/f47ac10b-58cc-4372-a567-0e02b2c3d479/verify/" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" \
  -H "Accept: application/json"
```

---

## 2. POST /api/todos/{id}/toggle/

Updates the completion state of a `MANUAL` checklist task for the authenticated agent.

- **Role**: `new_agent` or `manager` (see [Authentication](authentication.md))

### Parameters

| Parameter | In | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Path | UUID | Yes | — | Unique identifier of the `TodoItem`. |
| `done` | Body | Boolean | No | `true` | `true` to complete task; `false` to mark incomplete. |

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Task status updated | `{"todo_id": "<uuid>", "done": true, "done_at": "<iso>" \| null}` |
| **`400 Bad Request`** | No assigned template | `{"error": "No assigned template."}` |
| **`401 Unauthorized`** | Missing or invalid auth | `{"detail": "Authentication credentials were not provided."}` |
| **`404 Not Found`** | Todo not in agent's template | `{"detail": "No TodoItem matches the given query."}` or `{"error": "Agent profile not found."}` |

### Response Example (`200 OK` - Completed)

```json
{
  "todo_id": "b8a5d3f2-1234-5678-9abc-def012345678",
  "done": true,
  "done_at": "2026-09-16T08:45:00Z"
}
```

### Curl Examples (Local Dev)

```bash
# Mark task completed
curl -X POST "http://localhost:8000/api/todos/b8a5d3f2-1234-5678-9abc-def012345678/toggle/" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# Unmark task (reset)
curl -X POST "http://localhost:8000/api/todos/b8a5d3f2-1234-5678-9abc-def012345678/toggle/" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" \
  -H "Content-Type: application/json" \
  -d '{"done": false}'
```

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
