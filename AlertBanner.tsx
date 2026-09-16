import type { AlertState } from "../../types";

export interface AlertBannerProps {
  alert: AlertState | null;
  onDismiss: () => void;
}

const GLYPHS: Record<AlertState["kind"], string> = { success: "✓", error: "!", info: "i" };

/** Transient status banner, auto-dismissed by {@link useAlert} after a few seconds. */
export function AlertBanner({ alert, onDismiss }: AlertBannerProps) {
  if (!alert) return null;

  return (
    <div role="status" style={{ flex: "none", padding: "12px 18px 0" }}>
      <div className={`bn-alert bn-alert--${alert.kind}`} style={{ maxWidth: 1040, margin: "0 auto" }}>
        <span className="bn-alert__glyph" aria-hidden="true">
          {GLYPHS[alert.kind]}
        </span>
        <div className="bn-alert__body">
          <div className="bn-alert__title">{alert.title}</div>
          <div className="bn-alert__text">{alert.body}</div>
        </div>
        <button type="button" className="bn-alert__dismiss" aria-label="Dismiss message" onClick={onDismiss}>
          ×
        </button>
      </div>
    </div>
  );
}
