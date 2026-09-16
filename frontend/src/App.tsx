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

/**
 * App root. Renders the Dev Auth {@link LoginScreen} until a session
 * exists, then the shell (sidebar/tab bar + header) around the active
 * onboarding screen. State and side effects live in {@link useOnboarding}.
 */
export default function App() {
  const onboarding = useOnboarding();
  const {
    isAuthenticated,
    agent,
    devEmail,
    setDevEmail,
    loggingIn,
    signIn,
    signOut,
    screen,
    goToScreen,
    doneCount,
    totalCount,
    signatureAccepted,
    alert,
    dismissAlert,
  } = onboarding;

  if (!isAuthenticated) {
    return (
      <div className="bn-app-shell">
        <LoginScreen devEmail={devEmail} onDevEmailChange={setDevEmail} loggingIn={loggingIn} onSignIn={signIn} />
      </div>
    );
  }

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
