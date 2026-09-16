import type { OnboardingDocument } from "../../types";

export interface DocumentsListProps {
  documents: OnboardingDocument[];
}

/** Essential guides and charters, badged `[PDF]` / `[DOC]` / `[LIEN]` per `03-frontend-app.md`. */
export function DocumentsList({ documents }: DocumentsListProps) {
  if (documents.length === 0) return null;

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 11 }}>
      <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>Essential documents</h3>
      {documents.map((doc) => (
        <div key={doc.id} className="bn-resource-row">
          <span className="bn-resource-row__badge">{doc.format.toUpperCase()}</span>
          <div className="bn-resource-row__body">
            <div className="bn-resource-row__title">{doc.title}</div>
            <div className="bn-resource-row__subtitle">{hostnameOf(doc.url)}</div>
          </div>
          <a href={doc.url} target="_blank" rel="noopener noreferrer" className="bn-button bn-button--link">
            Open ↗
          </a>
        </div>
      ))}
    </section>
  );
}

function hostnameOf(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}
