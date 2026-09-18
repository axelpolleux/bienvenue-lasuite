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

export interface AgentProgress {
  totalTasks: number;
  completedTasks: number;
  percentage: number;
}

export interface Agent {
  id?: string;
  /** Full display name, e.g. "Alex Martin". */
  name: string;
  /** Institutional email — the primary identity key across every service. */
  email: string;
  role?: string;
  jobTitle?: string;
  phone?: string;
  arrivalDate?: string | null;
  departureDate?: string | null;
  serviceName?: string | null;
  serviceInitials?: string | null;
  serviceColor?: string | null;
  serviceLogoUrl?: string | null;
  managerName?: string | null;
  managerEmail?: string | null;
  signatureAccepted?: boolean;
  progress?: AgentProgress;
  createdAt?: string;
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
  /** Short presentation of the tool, shown under the task title. */
  description?: string;
  serviceLink: string;
  serviceName: string;
  /** Link to the tool's documentation, shown next to the access link. */
  docUrl?: string;
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
  role?: string;
  /** Service/department the colleague belongs to — drives their avatar colour. */
  department?: string;
  tchapLink: string;
  /** True when this person is on the new agent's own team. */
  team?: boolean;
}

export type ContactFilter = "All" | "My team";

/** One tile in the Home "first days" activity grid — static demo data, not tracked in the checklist. */
export interface HomeActivity {
  id: string;
  icon: "breakfast" | "meeting" | "equipment" | "tour";
  iconBg: string;
  label: string;
  dueLabel: string;
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

export interface OnboardingBundle {
  agent: Agent;
  template: Template | null;
  todos: TodoWithStatus[];
  colleagues: Colleague[];
  documents: OnboardingDocument[];
  trainings: Training[];
}

export interface AgentProfile {
  name?: string;
  jobTitle: string;
  department: string;
  organisation: string;
  phone: string;
}

export type ScreenId = "home" | "checklist" | "resources" | "contact" | "signature";

export type AlertKind = "success" | "error" | "info";

export interface AlertState {
  kind: AlertKind;
  title: string;
  body: string;
}

export type ResourceFilter = "All" | "Documents" | "Trainings";
