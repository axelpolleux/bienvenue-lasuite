import type { ChangeEvent } from "react";
import logo from "../../assets/bienvenue-logo.webp";

export interface LoginScreenProps {
	devEmail: string;
	onDevEmailChange: (email: string) => void;
	loggingIn: boolean;
	onSignInDev: () => void;
	onSignInKeycloak: () => void;
}

interface DevBypassProps {
	devEmail: string;
	onDevEmailChange: (email: string) => void;
	loggingIn: boolean;
	onSignInDev: () => void;
}

function DevBypassSection({ devEmail, onDevEmailChange, loggingIn, onSignInDev }: DevBypassProps) {
	return (
		<>
			<div style={{ display: "flex", alignItems: "center", gap: 12, margin: "2px 0" }}>
				<div style={{ flex: 1, height: 1, background: "var(--bn-color-border)" }} />
				<span style={{ font: "400 12px/1 var(--bn-font)", color: "var(--bn-color-ink-subtle)" }}>
					or continue in development mode
				</span>
				<div style={{ flex: 1, height: 1, background: "var(--bn-color-border)" }} />
			</div>

			<label className="bn-field">
				<span className="bn-field__label">Sign in as Dev Agent</span>
				<select
					className="bn-input"
					value={devEmail}
					onChange={(e: ChangeEvent<HTMLSelectElement>) => onDevEmailChange(e.target.value)}
				>
					<option value="alex.martin@gouv.fr">alex.martin@gouv.fr — new agent</option>
					<option value="lea.fontaine@gouv.fr">lea.fontaine@gouv.fr — new agent (fresh start)</option>
					<option value="agent@bienvenue.local">agent@bienvenue.local — Keycloak agent</option>
					<option value="manager@bienvenue.local">manager@bienvenue.local — Keycloak manager</option>
				</select>
				<span className="bn-field__help">
					Dev auth bypass — sends <code>X-Dev-User-Email</code>. In production this header is ignored and a valid Keycloak session is required.
				</span>
			</label>

			<button
				type="button"
				className="bn-button bn-button--secondary"
				aria-busy={loggingIn}
				onClick={onSignInDev}
			>
				{loggingIn && <span className="bn-spinner bn-spinner--dark" aria-hidden="true" />}
				{loggingIn ? "Signing in…" : "Sign in as Dev Agent"}
			</button>
		</>
	);
}

/**
 * Sign-in screen supporting ProConnect Keycloak SSO and local Dev Auth bypass.
 */
export function LoginScreen({
	devEmail,
	onDevEmailChange,
	loggingIn,
	onSignInDev,
	onSignInKeycloak,
}: LoginScreenProps) {
	return (
		<div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "28px 18px" }}>
			<div className="bn-card" style={{ width: "100%", maxWidth: 430, display: "flex", flexDirection: "column", gap: 20, animation: "bn-fade-in .3s ease both" }}>
				<img src={logo} alt="Bienvenue à La Suite" style={{ height: 40, width: "auto", alignSelf: "flex-start" }} />

				<div style={{ height: 1, background: "#e5e5e5" }} />

				<div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
					<h1 style={{ margin: 0, font: "700 32px/1.15 var(--bn-font)", color: "var(--bn-color-primary)", letterSpacing: "-.01em" }}>
						Bienvenue
					</h1>
					<p style={{ margin: 0, font: "400 15px/1.6 var(--bn-font)", color: "var(--bn-color-ink-muted)" }}>
						The connected onboarding kit for La Suite numérique. Sign in with your institutional account to open your checklist.
					</p>
				</div>

				<button type="button" className="bn-button" onClick={onSignInKeycloak}>
					Sign in with ProConnect (Keycloak SSO)
				</button>

				<DevBypassSection
					devEmail={devEmail}
					onDevEmailChange={onDevEmailChange}
					loggingIn={loggingIn}
					onSignInDev={onSignInDev}
				/>

				<p style={{ margin: 0, font: "400 12px/1.6 var(--bn-font)", color: "var(--bn-color-ink-subtle)", textAlign: "center" }}>
					ProConnect / Keycloak — sovereign single sign-on.
				</p>
			</div>
		</div>
	);
}


