import type { Agent, AgentProfile, HomeActivity } from "../types";

/**
 * Presentation helpers and dev bypass fixtures for the frontend.
 *
 * NOTE: All core onboarding data (tasks, checklists, colleagues, documents,
 * and completion progress) is dynamically served from the Django REST API
 * (GET /api/onboarding/me/). This file only retains UI presentation metadata.
 */

/**
 * Stands in for the agent record pulled from Grist (name, job title,
 * department, organisation, phone) that feeds the email signature. There is
 * no in-app editing screen — this data is read-only from the agent's point
 * of view, sourced from Grist once the real integration is wired up.
 */
export const SEED_PROFILE: AgentProfile = {
  jobTitle: "Project officer",
  department: "Digital Department",
  organisation: "Interministerial Digital Directorate",
  phone: "+33 1 71 21 01 70",
};

/** Static demo tiles for the Home "first days" activity grid (not part of the checklist). */
export const SEED_HOME_ACTIVITIES: HomeActivity[] = [
  { id: "a1", icon: "breakfast", iconBg: "#fceec9", label: "Team breakfast", dueLabel: "D+1" },
  { id: "a2", icon: "meeting", iconBg: "#e3e3fd", label: "Welcome meeting", dueLabel: "D+1" },
  { id: "a3", icon: "equipment", iconBg: "#d7f5e3", label: "Receiving my IT equipment", dueLabel: "D+1" },
  { id: "a4", icon: "tour", iconBg: "#fbe0f0", label: "Tour of my workplace", dueLabel: "D+1" },
];

/** Demo Dev Auth identities, mirroring `X-Dev-User-Email` (see `04-external-integrations.md`, section 2.2). */
export const DEV_AGENTS: Record<string, Agent & { seedDone: Record<string, boolean> }> = {
  "alex.martin@gouv.fr": { name: "Alex Martin", email: "alex.martin@gouv.fr", seedDone: { t5: true } },
  "lea.fontaine@gouv.fr": { name: "Léa Fontaine", email: "lea.fontaine@gouv.fr", seedDone: {} },
};
