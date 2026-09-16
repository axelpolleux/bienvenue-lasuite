# Authentication & Permissions

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)

---

Authentication mechanisms, user roles, and security policies governing the **Bienvenue à La Suite** REST API.

> [!IMPORTANT]
> **Single Source of Truth for Request Headers**: Individual endpoint reference pages specify only the required **Role**. Refer to this document for the exact request headers required in each environment.

---

## 1. Authentication Strategy

The API employs a dual authentication model based on Django's `DEBUG` setting:

| Mode | Condition | Header | Format / Example | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Development** | `DEBUG = True` | `X-Dev-User-Email` | `alex.martin@gouv.fr` | Resolves or creates an `Agent` on the fly for local testing without an external identity provider. |
| **Production** | `DEBUG = False` | `Authorization` | `Bearer <keycloak_jwt>` | Validates incoming OIDC JWT signature against Keycloak JWKS and extracts user claims. |

### Security Invariants & Guardrails

- **Strict Dev Header Rejection**: When `DEBUG = False`, the `X-Dev-User-Email` header is **strictly rejected and ignored**. All requests must provide a valid Bearer JWT.
- **Unauthorized Challenge**: Requests lacking credentials return HTTP `401 Unauthorized` with:
  ```http
  WWW-Authenticate: Bearer realm="api"
  ```
- **Invalid Tokens**: Malformed or expired JWT tokens return HTTP `401 Unauthorized`:
  ```json
  {
    "detail": "Invalid or expired Keycloak token."
  }
  ```

---

## 2. User Roles & Permission Matrix

The application differentiates between two user roles configured in `Agent.role`:

| Role | DRF Permission Class | Allowed Actions |
| :--- | :--- | :--- |
| **`new_agent`** | `IsAuthenticated` | - Retrieve own onboarding bundle (`GET /api/onboarding/me/`)<br>- Verify automated tasks (`POST /api/todos/{id}/verify/`)<br>- Toggle manual checklist items (`POST /api/todos/{id}/toggle/`)<br>- Accept official signature (`POST /api/signature/accept/`) |
| **`manager`** | `IsAuthenticated, IsManager` | - All actions available to `new_agent`<br>- Access newcomer overview dashboard (`GET /api/manager/overview/`)<br>- Reassign onboarding templates to agents (`PATCH /api/agents/{id}/assign-template/`) |

> [!NOTE]
> Manager endpoints enforce the DRF permission `IsManager`. When a `new_agent` requests a manager route, the API responds with `403 Forbidden`.

---

## 3. Request Header Examples

### Local Development (`DEBUG=True`)

```http
GET /api/onboarding/me/ HTTP/1.1
Host: localhost:8000
X-Dev-User-Email: alex.martin@gouv.fr
Accept: application/json
```

### Production / Staging (`DEBUG=False`)

```http
GET /api/onboarding/me/ HTTP/1.1
Host: api.bienvenue.numerique.gouv.fr
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
Accept: application/json
```

---

[API Index](README.md) · [Authentication](authentication.md) · [Onboarding](onboarding.md) · [Todos](todos.md) · [Manager](manager.md) · [Mock Suite](mock-suite.md)
