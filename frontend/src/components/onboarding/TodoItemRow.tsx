import { VALIDATION_HINTS, VALIDATION_TAGS, formatCompletionTimestamp } from "../../lib/onboarding";
import type { TodoWithStatus } from "../../types";

export interface TodoItemRowProps {
  todo: TodoWithStatus;
  busy: boolean;
  onVerify: () => void;
  onToggle: (next: boolean) => void;
  onOpenSignature: () => void;
}

/**
 * One row of the sequential checklist. `API_CHECK` steps call
 * `POST /api/todos/{id}/verify/` (here, {@link TodoItemRowProps.onVerify}),
 * `MANUAL` steps are self-declared, and `SIGNATURE` links to the dedicated
 * signature screen — see `03-frontend-app.md` section 4.1.
 */
export function TodoItemRow({ todo, busy, onVerify, onToggle, onOpenSignature }: TodoItemRowProps) {
  const cardModifier = todo.done ? " bn-todo--done" : todo.isLocked ? " bn-todo--locked" : "";
  const metaText = todo.done
    ? todo.doneAt
      ? `Completed ${formatCompletionTimestamp(todo.doneAt)}`
      : "Completed"
    : todo.isLocked
      ? "Waiting on an earlier step"
      : VALIDATION_HINTS[todo.validationType];

  return (
    <div className={`bn-todo${cardModifier}`} aria-disabled={todo.isLocked}>
      <div className="bn-todo__row">
        <span className="bn-todo__badge" aria-hidden="true">
          <TodoBadgeGlyph todo={todo} />
        </span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div className="bn-todo__label">{todo.label}</div>
          {todo.description && (
            <div style={{ font: "400 12.5px/1.5 var(--bn-font)", color: "var(--bn-color-ink-subtle)", marginTop: 2 }}>
              {todo.description}
            </div>
          )}
          <div className="bn-todo__meta">
            <span className="bn-todo__tag">{VALIDATION_TAGS[todo.validationType]}</span>
            <span className="bn-todo__meta-text">{metaText}</span>
          </div>
        </div>
      </div>

      {!todo.done && !todo.isLocked && (
        <div className="bn-todo__actions">
          {todo.validationType === "API_CHECK" && (
            <button type="button" className="bn-button" aria-busy={busy} onClick={onVerify}>
              {busy && <span className="bn-spinner" aria-hidden="true" />}
              {busy ? "Checking Fichiers…" : "Verify my Fichiers account"}
            </button>
          )}
          {todo.validationType === "MANUAL" && (
            <button type="button" className="bn-button" onClick={() => onToggle(true)}>
              Mark as done
            </button>
          )}
          {todo.validationType === "SIGNATURE" && (
            <button type="button" className="bn-button" onClick={onOpenSignature}>
              Open my signature
            </button>
          )}
          {todo.serviceLink && (
            <a href={todo.serviceLink} target="_blank" rel="noopener noreferrer" className="bn-button bn-button--link">
              Open {todo.serviceName} ↗
            </a>
          )}
          {todo.docUrl && (
            <a
              href={todo.docUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bn-button bn-button--link"
              style={{ marginLeft: "auto" }}
            >
              Ouvrir la documentation
            </a>
          )}
        </div>
      )}

      {todo.done && todo.validationType === "MANUAL" && (
        <div className="bn-todo__actions">
          <button type="button" className="bn-button bn-button--ghost" onClick={() => onToggle(false)}>
            Mark as not done
          </button>
          {todo.serviceLink && (
            <a href={todo.serviceLink} target="_blank" rel="noopener noreferrer" className="bn-button bn-button--link">
              Open {todo.serviceName} ↗
            </a>
          )}
          {todo.docUrl && (
            <a
              href={todo.docUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="bn-button bn-button--link"
              style={{ marginLeft: "auto" }}
            >
              Ouvrir la documentation
            </a>
          )}
        </div>
      )}

      {todo.isLocked && <div className="bn-todo__locked-note">Locked — complete step {todo.order - 1} first.</div>}
    </div>
  );
}

function TodoBadgeGlyph({ todo }: { todo: TodoWithStatus }) {
  if (todo.done) {
    return (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={2.1} strokeLinecap="round" strokeLinejoin="round">
        <path d="m3.2 8.4 3.2 3.2 6.4-7.2" />
      </svg>
    );
  }
  if (todo.isLocked) {
    return (
      <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round">
        <rect x="3.2" y="7" width="9.6" height="6.6" rx="1.2" />
        <path d="M5.6 7V5.2a2.4 2.4 0 0 1 4.8 0V7" />
      </svg>
    );
  }
  return <>{todo.order}</>;
}
