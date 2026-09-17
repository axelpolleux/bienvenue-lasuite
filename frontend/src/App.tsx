import { AlertBanner } from "./components/layout/AlertBanner";
import { Header } from "./components/layout/Header";
import { Sidebar } from "./components/layout/Sidebar";
import { TabBar } from "./components/layout/TabBar";
import { LoginScreen } from "./components/auth/LoginScreen";
import { useOnboarding } from "./hooks/useOnboarding";
import { ChecklistPage } from "./pages/ChecklistPage";
import { ContactPage } from "./pages/ContactPage";
import { HomePage } from "./pages/HomePage";
import { ResourcesPage } from "./pages/ResourcesPage";
import { SignaturePage } from "./pages/SignaturePage";
import type { ScreenId } from "./types";

const PAGE_COPY: Record<ScreenId, (doneCount: number, totalCount: number, signatureAccepted: boolean) => [string, string]> = {
  home: () => ["Home", ""],
  checklist: (doneCount, totalCount) => ["My checklist", `${doneCount} of ${totalCount} steps completed`],
  resources: () => ["Resources", "Documents and trainings"],
  contact: () => ["Contact", "People to reach on Tchap"],
  signature: (_d, _t, signatureAccepted) => ["Email signature", signatureAccepted ? "Confirmed" : "Awaiting your confirmation"],
};

function AuthenticatedApp({ onboarding }: { onboarding: ReturnType<typeof useOnboarding> }) {
	const { agent, screen, goToScreen, signOut, doneCount, totalCount, signatureAccepted, alert, dismissAlert } = onboarding;
	const [title, subtitle] = PAGE_COPY[screen](doneCount, totalCount, signatureAccepted);
	const remainingSteps = totalCount - doneCount;

	return (
		<div className="bn-app-shell bn-app-shell--split">
			<Sidebar agent={agent} activeScreen={screen} remainingSteps={remainingSteps} onNavigate={goToScreen} onSignOut={signOut} />
			<div className="bn-app-shell__body">
				<Header title={title} subtitle={subtitle} agentName={agent.name} />
				<AlertBanner alert={alert} onDismiss={dismissAlert} />
				<main className="bn-page">
					<div className="bn-page__inner">
						{screen === "home" && <HomePage onboarding={onboarding} />}
						{screen === "checklist" && <ChecklistPage onboarding={onboarding} />}
						{screen === "resources" && <ResourcesPage onboarding={onboarding} />}
						{screen === "contact" && <ContactPage onboarding={onboarding} />}
						{screen === "signature" && <SignaturePage onboarding={onboarding} />}
					</div>
				</main>
				<TabBar activeScreen={screen} remainingSteps={remainingSteps} onNavigate={goToScreen} />
			</div>
		</div>
	);
}

/**
 * App root. Renders initial loading probe, Dev/Keycloak login, or authenticated shell.
 */
export default function App() {
	const onboarding = useOnboarding();
	const { isAuthenticated, isLoadingInitial, devEmail, setDevEmail, loggingIn, signInDev, signInKeycloak } = onboarding;

	if (isLoadingInitial) {
		return (
			<div className="bn-app-shell" style={{ alignItems: "center", justifyContent: "center" }}>
				<span className="bn-spinner bn-spinner--dark" style={{ width: 32, height: 32, borderWidth: 3 }} aria-label="Loading" />
			</div>
		);
	}

	if (!isAuthenticated) {
		return (
			<div className="bn-app-shell">
				<AlertBanner alert={onboarding.alert} onDismiss={onboarding.dismissAlert} />
				<LoginScreen
					devEmail={devEmail}
					onDevEmailChange={setDevEmail}
					loggingIn={loggingIn}
					onSignInDev={() => signInDev(devEmail)}
					onSignInKeycloak={signInKeycloak}
				/>
			</div>
		);
	}

	return <AuthenticatedApp onboarding={onboarding} />;
}


