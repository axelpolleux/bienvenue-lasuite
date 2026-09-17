import { ActivityIcon } from "../components/onboarding/ActivityIcon";
import { ProgressBar } from "../components/onboarding/ProgressBar";
import { SEED_HOME_ACTIVITIES } from "../data/seed";
import { VALIDATION_HINTS } from "../lib/onboarding";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";

export interface HomePageProps {
  onboarding: UseOnboardingReturn;
}

/** Landing screen: progress hero, quick-stat tiles, first-days activities, and the current step. */
export function HomePage({ onboarding }: HomePageProps) {
  const { agent, currentStep, doneCount, totalCount, colleagues, documents, signatureAccepted, goToScreen } = onboarding;
  const firstName = agent.name.split(" ")[0] ?? "";
  const percentage = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;

  const tiles = [
    {
      label: "Steps remaining",
      value: String(totalCount - doneCount),
      hint: currentStep ? `Next: step ${currentStep.order}` : "All done",
      onClick: () => goToScreen("checklist"),
    },
    { label: "Colleagues to meet", value: String(colleagues.length), hint: "Reachable on Tchap", onClick: () => goToScreen("contact") },
    { label: "Documents", value: String(documents.length), hint: "Charters and guides", onClick: () => goToScreen("resources") },
    {
      label: "Signature",
      value: signatureAccepted ? "OK" : "To do",
      hint: signatureAccepted ? "Confirmed" : "Copy and confirm it",
      onClick: () => goToScreen("signature"),
    },
  ];

  return (
    <>
      <section className="bn-card bn-card--hero">
        <div style={{ flex: 1, minWidth: 250, display: "flex", flexDirection: "column", gap: 9 }}>
          <h2 style={{ margin: 0, font: "700 29px/1.2 var(--bn-font)" }}>Welcome, {firstName}</h2>
          <p style={{ margin: 0, font: "400 15px/1.6 var(--bn-font)", color: "#e4e4ff", maxWidth: "46ch" }}>
            Your onboarding runs step by step.
            <br />
            Complete each one to unlock the next.
          </p>
        </div>
        <div style={{ flex: "none", width: 238, maxWidth: "100%", display: "flex", flexDirection: "column", gap: 9 }}>
          <div style={{ display: "flex", justifyContent: "space-between", font: "500 13px/1 var(--bn-font)" }}>
            <span>Progress</span>
            <span>{percentage}%</span>
          </div>
          <ProgressBar percentage={percentage} onPrimarySurface />
          <div style={{ font: "400 12.5px/1.5 var(--bn-font)", color: "#c8c8ff" }}>
            {doneCount} of {totalCount} steps completed
          </div>
        </div>
      </section>

      <div className="bn-tile-grid">
        {tiles.map((tile) => (
          <button key={tile.label} type="button" className="bn-tile" onClick={tile.onClick}>
            <span className="bn-tile__label">{tile.label}</span>
            <span className="bn-tile__value">{tile.value}</span>
            <span className="bn-tile__hint">{tile.hint}</span>
          </button>
        ))}
      </div>

      <section className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 13 }}>
        <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>Your first days</h3>
        <div className="bn-activity-grid">
          {SEED_HOME_ACTIVITIES.map((activity) => (
            <div key={activity.id} className="bn-activity-card">
              <div className="bn-activity-card__top">
                <span className="bn-activity-card__icon" aria-hidden="true" style={{ background: activity.iconBg }}>
                  <ActivityIcon icon={activity.icon} />
                </span>
                <span className="bn-activity-card__badge">
                  <svg width="11" height="11" viewBox="0 0 18 18" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="2.5" y="3.5" width="13" height="12" rx="1.5" />
                    <path d="M2.5 7h13M6 2v3M12 2v3" />
                  </svg>
                  {activity.dueLabel}
                </span>
              </div>
              <div className="bn-activity-card__label">{activity.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 15 }}>
        <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>{currentStep ? "Your current step" : "Onboarding complete"}</h3>
        {currentStep ? (
          <>
            <div style={{ display: "flex", gap: 13, alignItems: "flex-start" }}>
              <span className="bn-todo__badge" aria-hidden="true">
                {currentStep.order}
              </span>
              <div style={{ minWidth: 0, display: "flex", flexDirection: "column", gap: 5 }}>
                <div style={{ font: "500 15.5px/1.45 var(--bn-font)" }}>{currentStep.label}</div>
                <div style={{ font: "400 13px/1.5 var(--bn-font)", color: "var(--bn-color-ink-subtle)" }}>
                  {VALIDATION_HINTS[currentStep.validationType]}
                </div>
              </div>
            </div>
            <button type="button" className="bn-button" style={{ alignSelf: "flex-start" }} onClick={() => goToScreen("checklist")}>
              Go to my checklist
            </button>
          </>
        ) : (
          <>
            <p style={{ margin: 0, font: "400 14.5px/1.6 var(--bn-font)", color: "var(--bn-color-ink-muted)" }}>
              Every step is complete. Your manager can see your onboarding as finished — the resources below stay
              available for reference.
            </p>
            <button type="button" className="bn-button bn-button--secondary" style={{ alignSelf: "flex-start" }} onClick={() => goToScreen("resources")}>
              Browse resources
            </button>
          </>
        )}
      </section>
    </>
  );
}
