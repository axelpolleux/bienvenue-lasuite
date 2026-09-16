import { ProgressBar } from "../components/onboarding/ProgressBar";
import { VALIDATION_HINTS } from "../lib/onboarding";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";

export interface HomePageProps {
  onboarding: UseOnboardingReturn;
}

/** Landing screen: progress hero, quick-stat tiles, and the current step. */
export function HomePage({ onboarding }: HomePageProps) {
  const { agent, template, currentStep, doneCount, totalCount, colleagues, documents, signatureAccepted, goToScreen } = onboarding;
  const firstName = agent.name.split(" ")[0] ?? "";
  const percentage = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;

  const tiles = [
    {
      label: "Steps remaining",
      value: String(totalCount - doneCount),
      hint: currentStep ? `Next: step ${currentStep.order}` : "All done",
      onClick: () => goToScreen("checklist"),
    },
    { label: "Colleagues to meet", value: String(colleagues.length), hint: "Reachable on Tchap", onClick: () => goToScreen("resources") },
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
          <div style={{ font: "500 12.5px/1.3 var(--bn-font)", color: "#c8c8ff", letterSpacing: ".06em" }}>{template.name}</div>
          <h2 style={{ margin: 0, font: "700 29px/1.2 var(--bn-font)" }}>Welcome, {firstName}</h2>
          <p style={{ margin: 0, font: "400 15px/1.6 var(--bn-font)", color: "#e4e4ff", maxWidth: "46ch" }}>
            Your onboarding runs step by step. Complete each one to unlock the next — we verify your La Suite accounts
            for you where we can.
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
