export interface ProgressBarProps {
  percentage: number;
  /** Set when the bar sits on the dark hero card, to use a light-on-dark track. */
  onPrimarySurface?: boolean;
  label?: string;
}

/** `role="progressbar"` onboarding-completion indicator. */
export function ProgressBar({ percentage, onPrimarySurface = false, label = "Onboarding progress" }: ProgressBarProps) {
  const trackClass = `bn-progress-track${onPrimarySurface ? " bn-progress-track--on-primary" : ""}`;
  const fillClass = `bn-progress-fill${onPrimarySurface ? " bn-progress-fill--on-primary" : ""}`;

  return (
    <div
      role="progressbar"
      aria-valuenow={percentage}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
      className={trackClass}
    >
      <div className={fillClass} style={{ width: `${percentage}%` }} />
    </div>
  );
}
