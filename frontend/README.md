# Bienvenue à La Suite — New Agent frontend (reformatted)

This is a reformatted version of the single-file `Bienvenue_App.html`
prototype, split into the component structure documented in
`03-frontend-app.md` and brought in line with the repository's
`AGENTS.md` conventions. It renders the **New Agent** screens only
(Login, Home, Checklist, Resources, Signature, Profile) — the Manager
dashboard from the architecture docs is not part of the source prototype
and is left as a follow-up.

## What changed, and why

- **One class component → many typed modules.** The original was a single
  ~300-line `Component extends DCLogic` class mixing state, side effects,
  and a giant `renderVals()` view-model. It is now:
  - `hooks/useOnboarding.ts` — state and actions (session, checklist,
    signature, profile), the local-prototype stand-in for the
    `useOnboarding.ts` / TanStack Query hook described in the frontend
    architecture doc.
  - `hooks/useLocalStorageState.ts`, `hooks/useAlert.ts` — small, reusable
    pieces of that state, each with one responsibility (AGENTS.md
    "Readability and design").
  - `lib/onboarding.ts`, `lib/navigation.ts` — pure, side-effect-free
    functions (sequential lock computation, signature text, formatting),
    easy to unit test in isolation.
  - `components/**` and `pages/**` — presentational pieces matching the
    directory layout in `03-frontend-app.md` section 2.
- **Inline `style="..."` strings → `styles/tokens.css`.** Component-level
  layout still uses a few inline styles for one-off spacing, but repeated
  visual patterns (buttons, cards, the checklist, alerts, forms) are now
  BEM-like `bn-*` classes over CSS custom properties, per AGENTS.md's CSS
  guidance and matching how `@gouvfr-lasuite/ui-tokens` is meant to be
  consumed once installed (see `main.tsx`).
- **Naming.** `camelCase` for variables/functions/hooks, `PascalCase` for
  components and types, no abbreviations that weren't already domain terms
  (`todo`, `Fichiers`, `Tchap`).
- **Docs.** Every exported function/component/hook has a short TSDoc
  comment stating its purpose and, where relevant, which backend endpoint
  or architecture-doc section it stands in for — so swapping the mock
  `checkFichiersAccount()` for a real `POST /api/todos/{id}/verify/` call
  later is a localized change.
- **Real logo.** `assets/bienvenue-logo.webp` (the uploaded wordmark)
  replaces the hand-drawn Marianne triband as the primary brand mark in
  the header, sidebar and login screen; the triband can be reintroduced
  as a small compliance mark once the app integrates with the official
  `@gouvfr-lasuite/ui-components` header.

## Backend integration

The frontend connects directly to the Django REST Framework BFF via `lib/api.ts` and `@tanstack/react-query`:

- Live onboarding data is fetched from `GET /api/onboarding/me/` and persisted in PostgreSQL.
- Task verification triggers real automated checks via `POST /api/todos/{id}/verify/`.
- Tasks can be toggled via `POST /api/todos/{id}/toggle/` and official signatures confirmed via `POST /api/signature/accept/`.
- SSO authentication is powered by Keycloak (ProConnect) via session cookies with CSRF protection, with a fallback `X-Dev-User-Email` bypass for local development.

## Directory map

```text
frontend/
├── index.html
├── README.md
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── assets/
    │   ├── bienvenue-logo.webp
    │   └── tools/
    ├── styles/
    │   └── tokens.css
    ├── types/
    │   └── index.ts
    ├── data/
    │   └── seed.ts
    ├── lib/
    │   ├── api.ts
    │   ├── onboarding.ts
    │   └── navigation.ts
    ├── hooks/
    │   ├── useOnboarding.ts
    │   ├── useAlert.ts
    │   └── useLocalStorageState.ts
    ├── components/
    │   ├── auth/LoginScreen.tsx
    │   ├── layout/Header.tsx
    │   ├── layout/Sidebar.tsx
    │   ├── layout/TabBar.tsx
    │   ├── layout/AlertBanner.tsx
    │   └── onboarding/
    │       ├── ProgressBar.tsx
    │       ├── TodoList.tsx
    │       ├── TodoItemRow.tsx
    │       ├── ColleaguesList.tsx
    │       ├── DocumentsList.tsx
    │       ├── TrainingList.tsx
    │       ├── SignatureInstructions.tsx
    │       └── SignatureBox.tsx
    └── pages/
        ├── HomePage.tsx
        ├── ChecklistPage.tsx
        ├── ResourcesPage.tsx
        ├── SignaturePage.tsx
        └── ContactPage.tsx
```

## Running it

```bash
npm install react react-dom
npm install -D vite @vitejs/plugin-react typescript @types/react @types/react-dom
npm run dev
```

(A `package.json` / `vite.config.ts` were not part of the uploaded
prototype and are intentionally left out here — drop these files into the
`frontend/` directory described in `05-local-development.md` and they
will slot into the existing Vite setup.)
