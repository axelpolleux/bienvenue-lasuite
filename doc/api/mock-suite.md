# Local Testing & Mock Suite Endpoints

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

Local mock endpoints simulating external services of **La Suite Numérique** (e.g. Nextcloud / Fichiers) for end-to-end integration and automated testing without external dependencies.

## Endpoints Summary

| Method | Path | Role | Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/mock-suite/fichiers/users/{email}/` | Public (Dev Mock) | [Simulate Fichiers user existence check (`?status=404` for unprovisioned)](#1-get-apimock-suitefichiersusersemail) |

---

## 1. GET /api/mock-suite/fichiers/users/{email}/

Simulates the user lookup endpoint of the **Fichiers** (Nextcloud) service queried by `suite_verifier.check_user_fichiers`.

- **Role**: Public (Dev Mock — no authentication required; intended for `DEBUG = True` local dev and tests)

### Parameters

| Parameter | In | Type | Required | Description |
| :--- | :--- | :--- | :--- | :--- |
| `email` | Path | String | Yes | Institutional email address (e.g. `alex.martin@gouv.fr`). |
| `status` | Query | String | No | Set `status=404` to simulate an unprovisioned or inactive account. |

### Responses

| Status | Condition | Response Preview |
| :--- | :--- | :--- |
| **`200 OK`** | Default (active account) | `{"exists": true, "email": "...", "service": "Fichiers / Nextcloud", "message": "User active and storage initialized."}` |
| **`404 Not Found`** | `?status=404` (unprovisioned) | `{"exists": false, "email": "...", "message": "User not found in local mock Fichiers service."}` |

### Response Example (`200 OK` - Active User)

```json
{
  "exists": true,
  "email": "alex.martin@gouv.fr",
  "service": "Fichiers / Nextcloud",
  "message": "User active and storage initialized."
}
```

### Response Example (`404 Not Found` - Unprovisioned User)

```json
{
  "exists": false,
  "email": "alex.martin@gouv.fr",
  "message": "User not found in local mock Fichiers service."
}
```

### Curl Examples (Local Dev)

```bash
# 1. Simulate active account (200 OK)
curl -X GET "http://localhost:8000/api/mock-suite/fichiers/users/alex.martin@gouv.fr/"

# 2. Simulate unprovisioned account (404 Not Found)
curl -X GET "http://localhost:8000/api/mock-suite/fichiers/users/alex.martin@gouv.fr/?status=404"
```

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
