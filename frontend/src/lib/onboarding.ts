import type { Agent, AgentProfile, TodoItem, TodoWithStatus, ValidationType } from "../types";

/** Human-readable explanation of how each validation type is resolved. */
export const VALIDATION_HINTS: Record<ValidationType, string> = {
  API_CHECK: "Verified automatically against the Fichiers service",
  MANUAL: "Self-declared — mark it done when you have finished",
  SIGNATURE: "Confirmed from the signature screen",
  GRIST: "Synchronised from Grist",
};

/** Short badge label shown next to each checklist step. */
export const VALIDATION_TAGS: Record<ValidationType, string> = {
  API_CHECK: "AUTO CHECK",
  MANUAL: "SELF-DECLARED",
  SIGNATURE: "SIGNATURE",
  GRIST: "GRIST",
};

/**
 * Applies the sequential-unlock rule from `03-frontend-app.md` (section 5):
 * step N+1 stays locked until step N is resolved.
 *
 * @param todos - Template steps, any order.
 * @param done - Map of `todoId -> completed` for MANUAL/API_CHECK steps.
 * @param doneAt - Map of `todoId -> ISO completion timestamp`.
 * @param signatureAccepted - Whether the SIGNATURE step has been confirmed.
 * @returns Steps sorted by `order`, each annotated with `done` and `isLocked`.
 */
export function computeTodoStatuses(
  todos: TodoItem[],
  done: Record<string, boolean>,
  doneAt: Record<string, string>,
  signatureAccepted: boolean,
): TodoWithStatus[] {
  const sorted = [...todos].sort((a, b) => a.order - b.order);
  let previousResolved = true;

  return sorted.map((todo) => {
    const isDone = todo.validationType === "SIGNATURE" ? signatureAccepted : !!done[todo.id];
    const isLocked = !previousResolved;
    if (!isDone) previousResolved = false;
    return { ...todo, done: isDone, doneAt: doneAt[todo.id] ?? null, isLocked };
  });
}

/** Finds the first step the agent still needs to resolve, if any. */
export function findCurrentStep(statuses: TodoWithStatus[]): TodoWithStatus | undefined {
  return statuses.find((t) => !t.done);
}

/** Builds the plain-text email signature from the template and the agent's profile. */
export function buildSignatureText(agent: Agent, profile: AgentProfile): string {
  const name = profile.name || agent.name;
  return [name, profile.jobTitle, profile.department, profile.organisation, "", agent.email, profile.phone].join("\n");
}

/** Formats an ISO timestamp as "16 Sep at 09:00", matching the reference prototype. */
export function formatCompletionTimestamp(iso: string | null): string {
  if (!iso) return "";
  const date = new Date(iso);
  const day = date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" });
  const time = date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  return `${day} at ${time}`;
}

/** Derives up to two initials from a full name, for avatar badges. */
export function initialsFor(fullName: string): string {
  return fullName
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}
