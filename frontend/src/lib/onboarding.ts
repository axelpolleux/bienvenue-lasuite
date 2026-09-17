import type { Agent, AgentProfile, TodoWithStatus, ValidationType } from "../types";
import { formatFrenchDateTime } from "./date";

/** Human-readable explanation of how each validation type is resolved. */
export const VALIDATION_HINTS: Record<ValidationType, string> = {
  API_CHECK: "Vérifié automatiquement auprès du service Fichiers",
  MANUAL: "Déclaratif — cochez l'étape dès qu'elle est réalisée",
  SIGNATURE: "Confirmé depuis l'écran de signature email",
  GRIST: "Synchronisé automatiquement depuis Grist",
};

/** Short badge label shown next to each checklist step. */
export const VALIDATION_TAGS: Record<ValidationType, string> = {
  API_CHECK: "CONTRÔLE AUTO",
  MANUAL: "DÉCLARATIF",
  SIGNATURE: "SIGNATURE",
  GRIST: "GRIST",
};

/** Finds the first step the agent still needs to resolve, if any. */
export function findCurrentStep(statuses: TodoWithStatus[]): TodoWithStatus | undefined {
  return statuses.find((t) => !t.done);
}

/** Builds the plain-text email signature from the template and the agent's profile. */
export function buildSignatureText(agent: Agent, profile: AgentProfile): string {
  const name = profile.name || agent.name;
  return [name, profile.jobTitle, profile.department, profile.organisation, "", agent.email, profile.phone].join("\n");
}

export function formatCompletionTimestamp(iso: string | null): string {
  return formatFrenchDateTime(iso);
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

/** Google Contacts-style palette: one background/text pair per avatar, picked deterministically from the name. */
const AVATAR_PALETTE: Array<{ bg: string; fg: string }> = [
  { bg: "#e3e3fd", fg: "#000091" },
  { bg: "#fde3e3", fg: "#c9184a" },
  { bg: "#d7f5e3", fg: "#18753c" },
  { bg: "#fceec9", fg: "#8a5a00" },
  { bg: "#fbe0f0", fg: "#a3195b" },
  { bg: "#dbeafe", fg: "#1e40af" },
  { bg: "#e9e3fd", fg: "#5b21b6" },
  { bg: "#dcf5f0", fg: "#0f766e" },
];

/** Deterministic avatar colour for a person, stable across renders (hashed from their name). */
export function avatarColorFor(name: string): { bg: string; fg: string } {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 31 + name.charCodeAt(i)) >>> 0;
  return AVATAR_PALETTE[hash % AVATAR_PALETTE.length];
}
