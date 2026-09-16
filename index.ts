/**
 * Domain types shared across the Bienvenue à La Suite frontend.
 *
 * These mirror the PostgreSQL schema described in `01-data-model.md` and the
 * REST payloads described in `02-backend-bff.md`, trimmed to what the New
 * Agent experience needs client-side. Field names use `camelCase` per
 * AGENTS.md, while the API itself may use `snake_case` — mapping happens in
 * the API client layer (out of scope for this local prototype).
 */

export type ValidationType = "API_CHECK" | "MANUAL" | "GRIST" | "SIGNATURE";

export interface Agent {
  /** Full display name, e.g. "Alex Martin". */
  name: string;
  /** Institutional email — the primary identity key across every service. */
  email: string;
}

export interface Template {
  id: string;
  name: string;
  /** Signature template text, interpolated with the agent's profile. */
  emailSignature: string;
}

export interface TodoItem {
  id: string;
  order: number;
  label: string;
  serviceLink: string;
  serviceName: string;
  validationType: ValidationType;
}

/** A `TodoItem` merged with the current agent's completion state. */
export interface TodoWithStatus extends TodoItem {
  done: boolean;
  doneAt: string | null;
  /** True when an earlier step in the sequence is not yet resolved. */
  isLocked: boolean;
}

export interface Colleague {
  id: string;
  name: string;
  role: string;
  tchapLink: string;
}

export type DocumentFormat = "pdf" | "doc" | "link";

export interface OnboardingDocument {
  id: string;
  title: string;
  url: string;
  format: DocumentFormat;
}

export interface Training {
  id: string;
  title: string;
  videoUrl: string;
  durationMinutes: number;
}

export interface AgentProfile {
  name?: string;
  jobTitle: string;
  department: string;
  organisation: string;
  phone: string;
}

export type ScreenId = "home" | "checklist" | "resources" | "signature" | "profile";

export type AlertKind = "success" | "error" | "info";

export interface AlertState {
  kind: AlertKind;
  title: string;
  body: string;
}

export type ResourceFilter = "All" | "People" | "Documents" | "Trainings";
