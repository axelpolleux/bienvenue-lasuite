# Local Development & Testing Guide

This guide describes how to run, develop, and test **Bienvenue à La Suite** in a completely self-contained local environment.

---

## 1. Prerequisites

- **Docker & Docker Compose** (Docker Desktop or Colima on macOS)
- **Python >= 3.14** with `uv` (for local backend development)
- **Node.js >= 20** with `pnpm` or `npm` (for local frontend development)

---

## 2. Environment Configuration

Copy the example environment file in `backend/`:

```bash
cp backend/.env.example backend/.env
```

Key environment variables in `backend/.env`:
```ini
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-local-dev-secret-key-bienvenue-42
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,backend
CORS_ALLOWED_ORIGINS=http://localhost:3000

# PostgreSQL Connection
DATABASE_URL=postgres://bienvenue:bienvenue@localhost:25432/bienvenue

# Grist Integration — pulled on demand via POST /api/manager/sync-grist/,
# no webhook/secret needed. Points at the team's cloud doc by default
# (docker-compose.yml); the self-hosted "grist" service is an offline
# fallback only, not the primary target.
GRIST_BASE_URL=https://docs.getgrist.com
GRIST_DOC_ID=your-grist-doc-id
GRIST_API_KEY=your-grist-api-key

# La Suite Service Verification (Defaults to built-in mock in dev)
LA_SUITE_FICHIERS_URL=http://localhost:8000/api/mock-suite/fichiers/users/{email}/
```

---

## 3. Running with Docker Compose

The simplest way to start the backend and database services together:

```bash
docker compose up --build
```

This starts:
- **PostgreSQL 16**: Port `25432` (`localhost:25432`)
- **Django BFF Backend**: Port `8000` (`http://localhost:8000`)

*(Note: In local development, the React Frontend is run directly via Vite on `http://localhost:3000` as described in Section 5 below.)*

---

## 4. Running Backend Locally (Without Docker)

If you prefer running Django locally for fast debugging:

1. **Start PostgreSQL only**:
   ```bash
   docker compose up -d postgresql
   ```

2. **Install dependencies and run migrations**:
   ```bash
   cd backend
   uv sync
   uv run python manage.py migrate
   ```

3. **Seed initial demo data (templates, mock agent)**:
   ```bash
   uv run python manage.py seed_demo_data
   ```

4. **Start the development server**:
   ```bash
   uv run python manage.py runserver 0.0.0.0:8000
   ```

---

## 5. Running Frontend Locally

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   # Installs React, TypeScript, Vite, and La Suite UI Kit (@gouvfr-lasuite/ui-components, @gouvfr-lasuite/ui-tokens)
   ```

2. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   Open `http://localhost:3000` in your browser.

---

## 6. Testing Key Flows Locally

### 6.1 Testing the "Fichiers" 200-OK Verification Step
The local mock endpoint simulates user existence in the Fichiers service:

```bash
# 1. Check verified state (Returns 200 OK)
curl -s http://localhost:8000/api/mock-suite/fichiers/users/alex.martin@gouv.fr/ | jq

# 2. Check unverified state (Returns 404 Not Found)
curl -s "http://localhost:8000/api/mock-suite/fichiers/users/unknown@gouv.fr/?status=404" | jq

# 3. Trigger verification via the BFF endpoint
curl -X POST http://localhost:8000/api/todos/<TODO_UUID>/verify/ \
  -H "Content-Type: application/json" \
  -H "X-Dev-User-Email: alex.martin@gouv.fr" | jq
```

### 6.2 Testing Grist Sync
Manager-triggered pull, no webhook — either via the API or the CLI:

```bash
# Via the API (requires a manager account)
curl -X POST http://localhost:8000/api/manager/sync-grist/ \
  -H "X-Dev-User-Email: camille.dupont@gouv.fr" | jq

# Or via the management command
docker compose exec backend python manage.py sync_grist
```

### 6.3 Switching Roles in Local Dev
In development mode, simply send the `X-Dev-User-Email` header to switch personas:
- **As New Agent**: `X-Dev-User-Email: alex.martin@gouv.fr`
- **As Manager**: `X-Dev-User-Email: camille.dupont@gouv.fr`
