import { avatarColorFor, initialsFor } from "../../lib/onboarding";
import type { Colleague } from "../../types";

export interface ColleaguesListProps {
  colleagues: Colleague[];
}

/** Key contacts for the new agent, each opening a Tchap conversation. */
export function ColleaguesList({ colleagues }: ColleaguesListProps) {
  if (colleagues.length === 0) return null;

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 11 }}>
      <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>Colleagues to meet</h3>
      {colleagues.map((colleague) => {
        const { bg, fg } = avatarColorFor(colleague.name);
        return (
          <div key={colleague.id} className="bn-resource-row">
            <span className="bn-resource-row__avatar" aria-hidden="true" style={{ background: bg, color: fg }}>
              {initialsFor(colleague.name)}
            </span>
            <div className="bn-resource-row__body">
              <div className="bn-resource-row__title">{colleague.name}</div>
              <div className="bn-resource-row__subtitle">{colleague.role}</div>
            </div>
            <a href={colleague.tchapLink} target="_blank" rel="noopener noreferrer" className="bn-button bn-button--secondary">
              Chat on Tchap ↗
            </a>
          </div>
        );
      })}
    </section>
  );
}
