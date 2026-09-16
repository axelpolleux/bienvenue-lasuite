import type { ChangeEvent } from "react";
import logo from "../../assets/bienvenue-logo.webp";

export interface LoginScreenProps {
  devEmail: string;
  onDevEmailChange: (email: string) => void;
  loggingIn: boolean;
  onSignIn: () => void;
}

/**
 * Dev Auth sign-in screen (see `04-external-integrations.md`, section 2.2).
 * In production this is replaced by a Keycloak/ProConnect redirect; here it
 * lets the person pick one of the two seeded demo identities.
 */
export function LoginScreen({ devEmail, onDevEmailChange, loggingIn, onSignIn }: LoginScreenProps) {
  function handleDevEmailChange(event: ChangeEvent<HTMLSelectElement>) {
    onDevEmailChange(event.target.value);
  }

  return (
    <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "28px 18px" }}>
      <div className="bn-card" style={{ width: "100%", maxWidth: 430, display: "flex", flexDirection: "column", gap: 24, animation: "bn-fade-in .3s ease both" }}>
        <img src={logo} alt="Bienvenue à La Suite" style={{ height: 40, width: "auto", alignSelf: "flex-start" }} />

        <div style={{ height: 1, background: "#e5e5e5" }} />

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          <h1 style={{ margin: 0, font: "700 32px/1.15 var(--bn-font)", color: "var(--bn-color-primary)", letterSpacing: "-.01em" }}>
            Bienvenue
          </h1>
          <p style={{ margin: 0, font: "400 15px/1.6 var(--bn-font)", color: "var(--bn-color-ink-muted)" }}>
            The connected onboarding kit for La Suite numérique. Sign in with your institutional account to open your
            checklist.
          </p>
        </div>

        <label className="bn-field">
          <span className="bn-field__label">Sign in as</span>
          <select className="bn-input" value={devEmail} onChange={handleDevEmailChange}>
            <option value="alex.martin@gouv.fr">alex.martin@gouv.fr — new agent</option>
            <option value="lea.fontaine@gouv.fr">lea.fontaine@gouv.fr — new agent (fresh start)</option>
          </select>
          <span className="bn-field__help">
            Dev auth bypass — sends <code>X-Dev-User-Email</code>. In production this header is ignored and a valid
            Keycloak JWT is required.
          </span>
        </label>

        <button type="button" className="bn-button" aria-busy={loggingIn} onClick={onSignIn}>
          {loggingIn && <span className="bn-spinner" aria-hidden="true" />}
          {loggingIn ? "Signing in…" : "Sign in with ProConnect"}
        </button>

        <p style={{ margin: 0, font: "400 12px/1.6 var(--bn-font)", color: "var(--bn-color-ink-subtle)", textAlign: "center" }}>
          ProConnect / Keycloak — sovereign single sign-on. Prototype: no real credentials are required.
        </p>
      </div>
    </div>
  );
}
