import type {
  Agent,
  AgentProfile,
  Colleague,
  HomeActivity,
  OnboardingDocument,
  Template,
  Training,
  TodoItem,
} from "../types";

/**
 * Static seed data standing in for `GET /api/onboarding/me/` while this
 * runs without the Django BFF (see `05-local-development.md`, section 6.1,
 * for the equivalent mock-service workflow on the backend). Replace this
 * module with `api/onboarding.ts` calls once the BFF is available; the
 * shapes below already match `TodoItem`, `Colleague`, etc.
 */

export const SEED_TEMPLATE: Template = {
  id: "e3b0c442-98fc-1c14-9af0-2a8b5f700001",
  name: "Common Administration Baseline",
  emailSignature: "{name} — {jobTitle}\n{department}\n{organisation}",
};

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

export const SEED_TODOS: TodoItem[] = [
  {
    id: "t1",
    order: 1,
    label: "Sign in to Docs and open your workspace",
    description: "Docs is La Suite's collaborative writing tool for notes, guides and shared documents.",
    serviceLink: "https://docs.numerique.gouv.fr",
    serviceName: "Docs",
    docUrl: "https://docs.numerique.gouv.fr/docs/0bbfe11d-2dd5-4c90-88ae-710e330f2152/",
    validationType: "MANUAL",
  },
  {
    id: "t2",
    order: 2,
    label: "Sign in to Tchap and join the general room",
    description: "Tchap is the secure instant messaging app used across the public administration.",
    serviceLink: "https://tchap.gouv.fr",
    serviceName: "Tchap",
    docUrl: "https://docs.numerique.gouv.fr/docs/1aec951f-c8d8-49c0-ab9e-9a1aac629b3e/",
    validationType: "MANUAL",
  },
  {
    id: "t3",
    order: 3,
    label: "Set up Visio and run a test meeting",
    description: "Visio is La Suite's video-conferencing tool for online meetings.",
    serviceLink: "https://visio.numerique.gouv.fr",
    serviceName: "Visio",
    docUrl: "https://docs.numerique.gouv.fr/docs/2157fe5a-3c64-4f83-bf6b-71dc083f383e/",
    validationType: "MANUAL",
  },
  {
    id: "t4",
    order: 4,
    label: "Sign in to Grist and check your workspace",
    description: "Grist is the spreadsheet-database tool used to manage structured team data.",
    serviceLink: "https://grist.numerique.gouv.fr",
    serviceName: "Grist",
    docUrl: "https://docs.numerique.gouv.fr/docs/db1ba377-d266-4eda-b77a-2931550eecbd/",
    validationType: "MANUAL",
  },
  {
    id: "t5",
    order: 5,
    label: "Activate and verify my Fichiers storage space",
    description: "Fichiers is your personal and shared file storage space.",
    serviceLink: "https://fichiers.numerique.gouv.fr",
    serviceName: "Fichiers",
    docUrl: "https://docs.numerique.gouv.fr/docs/0b8b54fb-ef03-48fa-99b8-b88a289ceb8c/",
    validationType: "API_CHECK",
  },
  {
    id: "t6",
    order: 6,
    label: "Sign in to France Transfert and check access",
    description: "France Transfert lets you securely send large files to people outside the administration.",
    serviceLink: "https://francetransfert.numerique.gouv.fr",
    serviceName: "France Transfert",
    docUrl: "https://docs.numerique.gouv.fr/docs/a3830491-b903-4565-a85b-ba5f55740527/",
    validationType: "MANUAL",
  },
  {
    id: "t7",
    order: 7,
    label: "Read the IT and security charter",
    serviceLink: "https://fichiers.numerique.gouv.fr/s/charter",
    serviceName: "Fichiers",
    validationType: "MANUAL",
  },
  {
    id: "t8",
    order: 8,
    label: "Validate my official email signature",
    serviceLink: "",
    serviceName: "",
    validationType: "SIGNATURE",
  },
];

export const SEED_COLLEAGUES: Colleague[] = [
  { id: "c1", name: "Camille Dupont", role: "IT referent", tchapLink: "https://tchap.gouv.fr/#/user/@camille.dupont:agent.gouv.fr", team: true },
  { id: "c2", name: "Isabelle Delatour", role: "Team lead — your manager", tchapLink: "https://tchap.gouv.fr/#/user/@isabelle.delatour:agent.gouv.fr", team: true },
  { id: "c3", name: "Karim Benali", role: "Technical referent", tchapLink: "https://tchap.gouv.fr/#/user/@karim.benali:agent.gouv.fr", team: true },
  { id: "c4", name: "Sophie Mercier", role: "Local HR contact", tchapLink: "https://tchap.gouv.fr/#/user/@sophie.mercier:agent.gouv.fr", team: false },
  { id: "c5", name: "Thomas Nguyen", role: "Onboarding buddy", tchapLink: "https://tchap.gouv.fr/#/user/@thomas.nguyen:agent.gouv.fr", team: true },
  { id: "c6", name: "Julie Lambert", role: "Project manager", tchapLink: "https://tchap.gouv.fr/#/user/@julie.lambert:agent.gouv.fr", team: true },
  { id: "c7", name: "Nicolas Petit", role: "Security officer", tchapLink: "https://tchap.gouv.fr/#/user/@nicolas.petit:agent.gouv.fr", team: false },
  { id: "c8", name: "Amel Haddad", role: "Communications lead", tchapLink: "https://tchap.gouv.fr/#/user/@amel.haddad:agent.gouv.fr", team: false },
  { id: "c9", name: "Marc Rousseau", role: "Facilities manager", tchapLink: "https://tchap.gouv.fr/#/user/@marc.rousseau:agent.gouv.fr", team: false },
  { id: "c10", name: "Elodie Bernard", role: "Data protection officer", tchapLink: "https://tchap.gouv.fr/#/user/@elodie.bernard:agent.gouv.fr", team: false },
];

/** Static demo tiles for the Home "first days" activity grid (not part of the checklist). */
export const SEED_HOME_ACTIVITIES: HomeActivity[] = [
  { id: "a1", icon: "breakfast", iconBg: "#fceec9", label: "Team breakfast", dueLabel: "D+7" },
  { id: "a2", icon: "meeting", iconBg: "#e3e3fd", label: "Welcome meeting", dueLabel: "D+7" },
  { id: "a3", icon: "equipment", iconBg: "#d7f5e3", label: "Receiving my IT equipment", dueLabel: "D+7" },
  { id: "a4", icon: "tour", iconBg: "#fbe0f0", label: "Tour of my workplace", dueLabel: "D+7" },
];

export const SEED_DOCUMENTS: OnboardingDocument[] = [
  { id: "d1", title: "IT and security charter", url: "https://fichiers.numerique.gouv.fr/s/charter", format: "pdf" },
  { id: "d2", title: "Welcome booklet", url: "https://docs.numerique.gouv.fr/docs/welcome-booklet", format: "doc" },
  { id: "d3", title: "Intranet home", url: "https://intranet.numerique.gouv.fr", format: "link" },
  { id: "d4", title: "Remote work agreement", url: "https://fichiers.numerique.gouv.fr/s/remote-work", format: "pdf" },
];

export const SEED_TRAININGS: Training[] = [
  { id: "v1", title: "Getting started with La Suite numérique", videoUrl: "https://tube.numerique.gouv.fr/w/getting-started", durationMinutes: 15 },
  { id: "v2", title: "Docs and Grist essentials", videoUrl: "https://tube.numerique.gouv.fr/w/docs-grist", durationMinutes: 22 },
  { id: "v3", title: "Tchap for teams", videoUrl: "https://tube.numerique.gouv.fr/w/tchap-teams", durationMinutes: 8 },
];

/** Demo Dev Auth identities, mirroring `X-Dev-User-Email` (see `04-external-integrations.md`, section 2.2). */
export const DEV_AGENTS: Record<string, Agent & { seedDone: Record<string, boolean> }> = {
  "alex.martin@gouv.fr": { name: "Alex Martin", email: "alex.martin@gouv.fr", seedDone: { t5: true } },
  "lea.fontaine@gouv.fr": { name: "Léa Fontaine", email: "lea.fontaine@gouv.fr", seedDone: {} },
};
