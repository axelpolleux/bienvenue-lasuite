import { useState, type FormEvent } from "react";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";
import type { AgentProfile } from "../types";

export interface ProfilePageProps {
  onboarding: UseOnboardingReturn;
}

const REQUIRED_FIELDS: Array<{ key: keyof AgentProfile; label: string }> = [
  { key: "name", label: "Full name" },
  { key: "jobTitle", label: "Job title" },
  { key: "department", label: "Department" },
  { key: "organisation", label: "Organisation" },
];

/** Identity details that feed the generated email signature. */
export function ProfilePage({ onboarding }: ProfilePageProps) {
  const { agent, profile, saveProfile, resetAll } = onboarding;
  const [draft, setDraft] = useState<AgentProfile>({ ...profile, name: profile.name || agent.name });
  const [error, setError] = useState("");
  const [saved, setSaved] = useState(false);
  const [resetConfirm, setResetConfirm] = useState(false);

  function updateField(key: keyof AgentProfile, value: string) {
    setDraft((previous) => ({ ...previous, [key]: value }));
    setError("");
    setSaved(false);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const missing = REQUIRED_FIELDS.filter((field) => !String(draft[field.key] ?? "").trim());
    if (missing.length > 0) {
      const names = missing.map((field) => field.label).join(", ");
      const verb = missing.length > 1 ? "are required — these fields appear" : "is required — it appears";
      setError(`${names} ${verb} in your official signature.`);
      return;
    }
    saveProfile(draft);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  function handleResetAll() {
    if (!resetConfirm) {
      setResetConfirm(true);
      return;
    }
    resetAll();
    setResetConfirm(false);
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 18 }}>
        <h3 style={{ margin: 0, font: "700 17px/1.2 var(--bn-font)" }}>My details</h3>
        <p style={{ margin: 0, font: "400 14px/1.6 var(--bn-font)", color: "var(--bn-color-ink-muted)", maxWidth: "62ch" }}>
          Email comes from your identity provider and cannot be changed here — it is the primary key across Keycloak,
          Grist and La Suite services. Everything else feeds your signature.
        </p>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
          <label className="bn-field">
            <span className="bn-field__label">Full name</span>
            <input className="bn-input" required value={draft.name ?? ""} onChange={(e) => updateField("name", e.target.value)} />
          </label>

          <label className="bn-field">
            <span className="bn-field__label">Institutional email</span>
            <input className="bn-input" readOnly value={agent.email} aria-describedby="email-help" />
            <span id="email-help" className="bn-field__help">
              Provided by Keycloak
            </span>
          </label>

          <label className="bn-field">
            <span className="bn-field__label">Job title</span>
            <input className="bn-input" required value={draft.jobTitle} onChange={(e) => updateField("jobTitle", e.target.value)} />
          </label>

          <label className="bn-field">
            <span className="bn-field__label">Department</span>
            <input className="bn-input" required value={draft.department} onChange={(e) => updateField("department", e.target.value)} />
          </label>

          <label className="bn-field">
            <span className="bn-field__label">Organisation</span>
            <input className="bn-input" required value={draft.organisation} onChange={(e) => updateField("organisation", e.target.value)} />
          </label>

          <label className="bn-field">
            <span className="bn-field__label">Phone</span>
            <input className="bn-input" inputMode="tel" value={draft.phone} onChange={(e) => updateField("phone", e.target.value)} />
          </label>
        </div>

        {error && (
          <div role="alert" className="bn-alert bn-alert--error">
            <span className="bn-alert__glyph" aria-hidden="true">
              !
            </span>
            <div className="bn-alert__text">{error}</div>
          </div>
        )}

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button type="submit" className="bn-button">
            {saved ? "Saved ✓" : "Save details"}
          </button>
          <button type="button" className="bn-button bn-button--ghost" onClick={() => setDraft({ ...profile, name: profile.name || agent.name })}>
            Reset changes
          </button>
        </div>
      </form>

      <section className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 13 }}>
        <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>Prototype data</h3>
        <p style={{ margin: 0, font: "400 13.5px/1.6 var(--bn-font)", color: "var(--bn-color-ink-subtle)", maxWidth: "60ch" }}>
          Progress and profile changes persist in this browser, standing in for PostgreSQL via the Django BFF.
          Resetting clears your local checklist statuses and restores the seeded template.
        </p>
        <button type="button" className="bn-button bn-button--danger" style={{ alignSelf: "flex-start" }} onClick={handleResetAll}>
          {resetConfirm ? "Tap again to confirm reset" : "Reset prototype data"}
        </button>
      </section>
    </>
  );
}
