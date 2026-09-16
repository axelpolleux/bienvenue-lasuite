# Frontend Application Architecture

This document defines the architecture, component structure, state management, and accessibility standards for the React Mini App located in `frontend/`.

The frontend is built using the official **La Suite numérique UI Kit** ([`suitenumerique/ui-kit`](https://github.com/suitenumerique/ui-kit)), ensuring seamless visual consistency, design tokens, and RGAA accessibility with the rest of _La Suite Numérique_.

---

## 1. Technology Choices

- **Runtime & Bundler**: React 18 / 19 with TypeScript, powered by **Vite**.
- **Design System & UI Library**: **La Suite UI Kit** via [`@gouvfr-lasuite/ui-components`](https://github.com/suitenumerique/ui-kit) and design tokens from [`@gouvfr-lasuite/ui-tokens`](https://github.com/suitenumerique/ui-kit) (built on Cunningham).
- **Design System Reference**: [La Suite UI Kit Storybook](https://suitenumerique.github.io/ui-kit/) & [GitHub repository](https://github.com/suitenumerique/ui-kit).
- **Server State & Data Fetching**: **TanStack Query** (React Query) for caching, optimistic updates, and background refetching.

---

## 2. Directory Structure

```text
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── src/
    ├── main.tsx               # Root entrypoint wrapping CunninghamProvider
    ├── App.tsx                # App shell, routing, dev user switcher
    ├── api/                   # Typed API client and endpoint callers
    │   ├── client.ts          # Axios / Fetch wrapper with auth headers
    │   ├── onboarding.ts      # Agent onboarding endpoints
    │   └── manager.ts         # Manager dashboard endpoints
    ├── types/                 # Shared TypeScript models & interfaces
    │   └── index.ts           # Agent, Template, TodoItem, etc.
    ├── hooks/                 # Custom data hooks
    │   ├── useOnboarding.ts   # React Query hook for /api/onboarding/me/
    │   └── useManager.ts      # React Query hook for /api/manager/overview/
    ├── components/
    │   ├── layout/
    │   │   ├── Header.tsx     # La Suite header & user status
    │   │   ├── Footer.tsx     # Legal notices & RGAA accessibility statement
    │   │   └── DevBar.tsx     # Debug bar to switch users in local dev
    │   ├── onboarding/
    │   │   ├── ProgressBar.tsx      # Visual & screen-reader progress indicator
    │   │   ├── TodoList.tsx         # Sequential task container
    │   │   ├── TodoItemRow.tsx      # Single task with verification button
    │   │   ├── ColleaguesList.tsx   # Team contact cards with Tchap links
    │   │   ├── DocumentsList.tsx    # Essential guides & download links
    │   │   ├── TrainingList.tsx     # Curated video players
    │   │   └── SignatureBox.tsx     # Email signature preview, copy & confirm
    │   └── manager/
    │       ├── ManagerTable.tsx     # Agent progress list & status badges
    │       └── TemplateSelector.tsx # Reassign template modal
    └── styles/
        └── tokens.css         # Scoped Cunningham token overrides
```

---

## 3. UI Kit Integration (`main.tsx`)

The application wraps the component tree in `CunninghamProvider` to configure design tokens, official Marianne typography, Material icons, and French locales:

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { CunninghamProvider } from "@gouvfr-lasuite/ui-components";
import "@gouvfr-lasuite/ui-components/style";
import "@gouvfr-lasuite/ui-components/fonts/marianne";
import "@gouvfr-lasuite/ui-components/fonts/material-icons";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <CunninghamProvider currentLocale="fr-FR" theme="default">
      <App />
    </CunninghamProvider>
  </React.StrictMode>,
);
```

### 3.1 Theming & Design Tokens (`@gouvfr-lasuite/ui-tokens`)

- **Tokens Engine**: Cunningham design tokens are scoped under CSS variables prefixed with `--c--` (e.g. `--c--theme--colors--primary-500`, `--c--components--button--...`).
- **Theme Selection**: Setting `theme="default"` applies `cunningham-theme--default` to `:root`. Custom themes can be defined in `cunningham.ts` and compiled using `npx cunningham -g css,scss,ts -o src`.
- **Locale Handling**: `currentLocale="fr-FR"` automatically localizes built-in strings across modals, date pickers, and alerts.
- **Component Reference**: Component documentation, props, and live interactive examples are available in the [La Suite UI Kit Storybook](https://suitenumerique.github.io/ui-kit/).

---

## 4. Core UI Flows

### 4.1 New Agent View

1. **Header & Welcome Banner**: Displays the agent's name, assigned department/template, and overall completion percentage.
2. **Progress Bar**: High-contrast, semantic progress bar using `ProgressBar` from `@gouvfr-lasuite/ui-components` (`role="progressbar"` with `aria-valuenow`).
3. **Sequential Todo Checklist**:
   - **Active Step**: Displayed with clear focus and action button.
     - If `validation_type === 'API_CHECK'` (Step 1 - Fichiers): Renders a **"Vérifier mon compte Fichiers"** `Button` from `@gouvfr-lasuite/ui-components` that sends `POST /api/todos/{id}/verify/`. Displays a loading spinner during the request and an `Alert` upon receiving HTTP 200.
     - If `validation_type === 'MANUAL'`: Renders a `Checkbox` from `@gouvfr-lasuite/ui-components` to mark completion.
   - **Completed Steps**: Displayed with a check icon, timestamp, and strikethrough styling.
   - **Locked Steps**: Displayed with a padlock icon, disabled interactions, and an `aria-disabled="true"` attribute indicating that previous steps must be completed first.
4. **Side Resources**:
   - **Colleagues**: `UserRow` and `UserAvatar` components from `@gouvfr-lasuite/ui-components` opening Tchap discussions.
   - **Documents**: Tagged `Badge` components (`[PDF]`, `[DOC]`, `[LIEN]`) for internal guides.
   - **Trainings**: Video duration badge and curated video player (`VideoPlayer` from `@gouvfr-lasuite/ui-components`).
5. **Signature Step**:
   - Live rendered box of their standardized email signature.
   - **"Copier la signature"** button with clipboard feedback.
   - **"Valider la configuration de ma signature"** button updating `signature_accepted = true`.

### 4.2 Manager View

1. **Summary Cards**: Total agents onboarding, completed onboardings, and agents waiting on verification.
2. **Data Table**:
   - Columns: Agent Name, Email, Assigned Template, Progress %, Signature Status, Current Active Step.
   - Action dropdown: "Changer de modèle" (opens template assignment modal).

---

## 5. Sequential Step Locking Logic

The frontend enforces strict progression order using task `order`:

```typescript
// Computes lock state for each task in the sequential list
export function calculateTodoLockStates(
  todos: TodoItem[],
): (TodoItem & { isLocked: boolean })[] {
  const sorted = [...todos].sort((a, b) => a.order - b.order);
  let previousDone = true;

  return sorted.map((todo) => {
    const isLocked = !previousDone;
    if (!todo.done) {
      previousDone = false; // All subsequent tasks are locked
    }
    return { ...todo, isLocked };
  });
}
```

---

<a id="rgaa-accessibility"></a>

## 6. Accessibility (RGAA 4.1 / WCAG 2.1 AA) & La Suite UI Kit

The frontend uses [`@gouvfr-lasuite/ui-components`](https://github.com/suitenumerique/ui-kit) components which are designed to comply with French public administration digital accessibility obligations
`.

### 6.2 Component Mappings from `@gouvfr-lasuite/ui-components`

- **`Button`**: Primary action buttons for Fichiers verification and signature validation.
- **`Checkbox`**: Self-declaration checkboxes for manual steps.
- **`Badge`**: Status tags for completed, pending, or locked steps and document formats (`[PDF]`, `[DOC]`, `[LIEN]`).
- **`Alert`**: Real-time feedback alerts for verification success and error states.
- **`Modal` / `ConfirmationModal`**: Manager template assignment dialog and confirmation prompts.
- **`ProgressBar`**: Semantic, accessible progress bar component reflecting completion percentage.
- **`UserRow` / `UserAvatar`**: Colleague contact rows with avatar and direct Tchap chat links.
- _Card Surfaces & Containers_: `@gouvfr-lasuite/ui-components` does not export a monolithic `<Card>` component; card surfaces and resource blocks are composed using semantic HTML (`<article>` / `<div>` or `LabelledBox`) styled with Cunningham design tokens (`tokens.css` / `--c--...`).
