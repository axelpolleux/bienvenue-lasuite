import type {
  Agent,
  Colleague,
  DocumentFormat,
  OnboardingBundle,
  OnboardingDocument,
  Template,
  TodoWithStatus,
  Training,
  ValidationType,
} from "../types";

/**
 * Extracts Django CSRF token from browser document cookie.
 */
export function getCsrfToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

interface RequestOptions extends RequestInit {
  devEmail?: string;
}

/**
 * Common fetch wrapper handling credentials, CSRF, and dev headers.
 */
async function apiFetch<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { devEmail, headers: customHeaders, ...fetchOptions } = options;
  const method = (fetchOptions.method || "GET").toUpperCase();

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(customHeaders as Record<string, string>),
  };

  if (fetchOptions.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  if (devEmail) {
    headers["X-Dev-User-Email"] = devEmail;
  }

  if (method !== "GET") {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      headers["X-CSRFToken"] = csrfToken;
    }
  }

  const response = await fetch(endpoint, {
    ...fetchOptions,
    headers,
    credentials: "include",
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errJson = await response.json();
      errorDetail = errJson.error || errJson.detail || JSON.stringify(errJson);
    } catch {
      // Keep statusText when JSON body is missing or unparseable
    }
    throw new Error(`API error (${response.status}): ${errorDetail}`);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

interface RawAgentProgress {
  total_tasks: number;
  completed_tasks: number;
  percentage: number;
}

interface RawAgent {
  id?: string;
  email: string;
  name: string;
  role?: string;
  signature_accepted?: boolean;
  created_at?: string;
  progress?: RawAgentProgress;
}

interface RawTemplate {
  id: string;
  name: string;
  email_signature: string;
  created_at?: string;
  updated_at?: string;
}

interface RawTodoItemWithStatus {
  id: string;
  order: number;
  label: string;
  service_link: string | null;
  service_name?: string;
  doc_url?: string | null;
  description?: string;
  validation_type: ValidationType;
  done: boolean;
  done_at: string | null;
  is_locked: boolean;
}

interface RawColleague {
  id: string;
  name: string;
  role?: string;
  tchap_link: string;
}

interface RawDocument {
  id: string;
  title: string;
  url: string;
  format: DocumentFormat;
}

interface RawTraining {
  id: string;
  title: string;
  video_url: string;
  duration_minutes: number;
}

interface RawOnboardingBundle {
  agent: RawAgent;
  template: RawTemplate | null;
  todos: RawTodoItemWithStatus[];
  colleagues: RawColleague[];
  documents: RawDocument[];
  trainings: RawTraining[];
}

function resolveServiceName(rawName?: string, serviceLink?: string | null): string {
  if (rawName && rawName.trim().length > 0) return rawName;
  if (!serviceLink) return "";
  const lower = serviceLink.toLowerCase();
  if (lower.includes("docs")) return "Docs";
  if (lower.includes("tchap")) return "Tchap";
  if (lower.includes("visio")) return "Visio";
  if (lower.includes("grist")) return "Grist";
  if (lower.includes("fichiers")) return "Fichiers";
  if (lower.includes("francetransfert")) return "France Transfert";
  if (lower.includes("webinaire")) return "Webinaire";
  return "Service";
}

function mapTodo(raw: RawTodoItemWithStatus): TodoWithStatus {
  return {
    id: raw.id,
    order: raw.order,
    label: raw.label,
    description: raw.description || undefined,
    serviceLink: raw.service_link || "",
    serviceName: resolveServiceName(raw.service_name, raw.service_link),
    docUrl: raw.doc_url || undefined,
    validationType: raw.validation_type,
    done: Boolean(raw.done),
    doneAt: raw.done_at,
    isLocked: Boolean(raw.is_locked),
  };
}

function mapColleague(raw: RawColleague): Colleague {
  let name = raw.name;
  let role = raw.role;
  if (!role && name.includes("(") && name.endsWith(")")) {
    const match = name.match(/^(.*?)\s*\((.*?)\)$/);
    if (match) {
      name = match[1].trim();
      role = match[2].trim();
    }
  }

  let department = "Général";
  if (role) {
    const r = role.toLowerCase();
    if (r.includes("it") || r.includes("technic") || r.includes("network") || r.includes("security")) {
      department = "IT & Digital";
    } else if (r.includes("team lead") || r.includes("manager") || r.includes("buddy") || r.includes("deputy")) {
      department = "Management";
    } else if (r.includes("hr") || r.includes("communication") || r.includes("recruitment")) {
      department = "HR & Communications";
    } else if (r.includes("facilities") || r.includes("data protection") || r.includes("office")) {
      department = "Facilities & Data Protection";
    }
  }

  const teamMembers = ["camille dupont", "isabelle delatour", "karim benali", "thomas nguyen", "julie lambert", "léa fontaine"];
  const isTeam = teamMembers.includes(name.toLowerCase());

  return {
    id: raw.id,
    name,
    role: role || undefined,
    department,
    tchapLink: raw.tchap_link,
    team: isTeam,
  };
}

function mapDocument(raw: RawDocument): OnboardingDocument {
  return {
    id: raw.id,
    title: raw.title,
    url: raw.url,
    format: raw.format,
  };
}

function mapTraining(raw: RawTraining): Training {
  return {
    id: raw.id,
    title: raw.title,
    videoUrl: raw.video_url,
    durationMinutes: raw.duration_minutes,
  };
}

function mapAgent(raw: RawAgent): Agent {
  return {
    id: raw.id,
    name: raw.name,
    email: raw.email,
    role: raw.role,
    signatureAccepted: raw.signature_accepted,
    progress: raw.progress
      ? {
          totalTasks: raw.progress.total_tasks,
          completedTasks: raw.progress.completed_tasks,
          percentage: raw.progress.percentage,
        }
      : undefined,
    createdAt: raw.created_at,
  };
}

function mapTemplate(raw: RawTemplate | null): Template | null {
  if (!raw) return null;
  return {
    id: raw.id,
    name: raw.name,
    emailSignature: raw.email_signature || "",
  };
}

function mapBundle(raw: RawOnboardingBundle): OnboardingBundle {
  return {
    agent: mapAgent(raw.agent),
    template: mapTemplate(raw.template),
    todos: (raw.todos || []).map(mapTodo),
    colleagues: (raw.colleagues || []).map(mapColleague),
    documents: (raw.documents || []).map(mapDocument),
    trainings: (raw.trainings || []).map(mapTraining),
  };
}

/**
 * Fetches current agent's onboarding bundle from BFF.
 */
export async function fetchOnboardingBundle(devEmail?: string): Promise<OnboardingBundle> {
  const raw = await apiFetch<RawOnboardingBundle>("/api/onboarding/me/", {
    method: "GET",
    devEmail,
  });
  return mapBundle(raw);
}

interface RawVerifyResponse {
  todo_id: string;
  done: boolean;
  done_at: string;
  message?: string;
}

/**
 * Triggers backend automated verification for an API_CHECK task.
 */
export async function verifyTodoTask(
  todoId: string,
  devEmail?: string,
): Promise<{ todoId: string; done: boolean; doneAt: string }> {
  const raw = await apiFetch<RawVerifyResponse>(`/api/todos/${todoId}/verify/`, {
    method: "POST",
    devEmail,
  });
  return {
    todoId: raw.todo_id,
    done: raw.done,
    doneAt: raw.done_at,
  };
}

interface RawToggleResponse {
  todo_id: string;
  done: boolean;
  done_at: string | null;
}

/**
 * Toggles completion status for a MANUAL task.
 */
export async function toggleTodoTask(
  todoId: string,
  done: boolean,
  devEmail?: string,
): Promise<{ todoId: string; done: boolean; doneAt: string | null }> {
  const raw = await apiFetch<RawToggleResponse>(`/api/todos/${todoId}/toggle/`, {
    method: "POST",
    devEmail,
    body: JSON.stringify({ done }),
  });
  return {
    todoId: raw.todo_id,
    done: raw.done,
    doneAt: raw.done_at,
  };
}

interface RawSignatureResponse {
  signature_accepted: boolean;
  message?: string;
}

/**
 * Confirms email signature validation for authenticated agent.
 */
export async function acceptSignatureTask(
  devEmail?: string,
): Promise<{ signatureAccepted: boolean }> {
  const raw = await apiFetch<RawSignatureResponse>("/api/signature/accept/", {
    method: "POST",
    devEmail,
  });
  return {
    signatureAccepted: raw.signature_accepted,
  };
}
