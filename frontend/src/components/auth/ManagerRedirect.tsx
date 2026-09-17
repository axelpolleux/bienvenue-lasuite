import { useEffect, useState } from "react";

export interface ManagerRedirectProps {
	targetUrl: string;
	onContinueToApp: () => void;
}

const REDIRECT_DELAY_MS = 1500;

/**
 * Transitional screen shown to managers right after login: auto-navigates to
 * Grist (where templates are edited) after a short delay, but never blocks —
 * a manager can cancel and open the regular Bienvenue app instead.
 */
export function ManagerRedirect({ targetUrl, onContinueToApp }: ManagerRedirectProps) {
	const [cancelled, setCancelled] = useState(false);

	useEffect(() => {
		if (cancelled) return;
		const timer = window.setTimeout(() => {
			window.location.href = targetUrl;
		}, REDIRECT_DELAY_MS);
		return () => window.clearTimeout(timer);
	}, [cancelled, targetUrl]);

	return (
		<div className="bn-app-shell" style={{ alignItems: "center", justifyContent: "center", textAlign: "center", gap: 18 }}>
			<span className="bn-spinner bn-spinner--dark" style={{ width: 32, height: 32, borderWidth: 3 }} aria-label="Redirecting" />
			<div>
				<p style={{ margin: 0, fontWeight: 500 }}>Redirecting to Grist…</p>
				<p style={{ margin: "4px 0 0", color: "var(--bn-color-ink-subtle)" }}>
					That's where you manage onboarding templates.
				</p>
			</div>
			<div style={{ display: "flex", gap: 10 }}>
				<a href={targetUrl} className="bn-button">
					Open Grist now
				</a>
				<button
					type="button"
					className="bn-button bn-button--secondary"
					onClick={() => {
						setCancelled(true);
						onContinueToApp();
					}}
				>
					Go to Bienvenue instead
				</button>
			</div>
		</div>
	);
}
