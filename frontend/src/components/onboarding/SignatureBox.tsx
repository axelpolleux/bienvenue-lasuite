import { useState } from "react";
import type { Agent, AgentProfile } from "../../types";

const COPY_FEEDBACK_MS = 2200;

export interface SignatureBoxProps {
  agent: Agent;
  profile: AgentProfile;
  accepted: boolean;
  /** True when an earlier checklist step must be resolved before confirming. */
  locked: boolean;
  accepting: boolean;
  onAccept: () => void;
}

/**
 * Live-rendered official email signature with a copy button and the final
 * "Valider ma signature" confirmation (`POST /api/signature/accept/`).
 */
export function SignatureBox({ agent, profile, accepted, locked, accepting, onAccept }: SignatureBoxProps) {
  const [copied, setCopied] = useState(false);
  const displayName = profile.name || agent.name;

  async function handleCopy() {
    const text = [displayName, profile.jobTitle, profile.department, profile.organisation, "", agent.email, profile.phone].join("\n");
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // Clipboard API may be unavailable; still show feedback so the person can select the text manually.
    }
    setCopied(true);
    setTimeout(() => setCopied(false), COPY_FEEDBACK_MS);
  }

  return (
    <section className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ margin: 0, font: "700 17px/1.2 var(--bn-font)" }}>Your official email signature</h3>
        <span
          style={{
            font: "700 11px/1 var(--bn-font)",
            letterSpacing: ".04em",
            padding: "6px 9px",
            borderRadius: 3,
            background: accepted ? "var(--bn-color-success-bg)" : "var(--bn-color-error-bg)",
            color: accepted ? "var(--bn-color-success)" : "var(--bn-color-error)",
          }}
        >
          {accepted ? "CONFIRMED" : "NOT CONFIRMED"}
        </span>
      </div>

      <p style={{ margin: 0, font: "400 14px/1.6 var(--bn-font)", color: "var(--bn-color-ink-muted)", maxWidth: "62ch" }}>
        Copy it into your mail client, then confirm the setup to close the final step.
      </p>

      <div className="bn-signature-preview">
        <div className="bn-marianne-block" aria-hidden="true">
          <span className="bn-marianne-block__bar bn-marianne-block__bar--blue" />
          <span className="bn-marianne-block__bar bn-marianne-block__bar--white" />
          <span className="bn-marianne-block__bar bn-marianne-block__bar--red" />
        </div>
        <div style={{ flex: 1, minWidth: 190, display: "flex", flexDirection: "column", gap: 3 }}>
          <div className="bn-signature-preview__name">{displayName}</div>
          <div className="bn-signature-preview__line">{profile.jobTitle}</div>
          <div className="bn-signature-preview__line">{profile.department}</div>
          <div className="bn-signature-preview__line">{profile.organisation}</div>
          <div style={{ height: 7 }} />
          <div className="bn-signature-preview__email">{agent.email}</div>
          <div className="bn-signature-preview__line">{profile.phone}</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button type="button" className="bn-button bn-button--secondary" onClick={handleCopy}>
          {copied ? "Copied to clipboard ✓" : "Copy signature"}
        </button>
        {!accepted && !locked && (
          <button type="button" className="bn-button" aria-busy={accepting} onClick={onAccept}>
            {accepting && <span className="bn-spinner" aria-hidden="true" />}
            {accepting ? "Confirming…" : "Confirm my signature setup"}
          </button>
        )}
      </div>

      {!accepted && locked && (
        <div className="bn-todo__locked-note">
          You can copy the signature now, but confirming it is the last step — finish the earlier checklist items
          first.
        </div>
      )}
    </section>
  );
}
