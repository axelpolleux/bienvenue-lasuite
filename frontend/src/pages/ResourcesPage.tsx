import { useMemo, useState } from "react";
import { ColleaguesList } from "../components/onboarding/ColleaguesList";
import { DocumentsList } from "../components/onboarding/DocumentsList";
import { TrainingList } from "../components/onboarding/TrainingList";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";
import type { ResourceFilter } from "../types";

export interface ResourcesPageProps {
  onboarding: UseOnboardingReturn;
}

const FILTERS: ResourceFilter[] = ["All", "People", "Documents", "Trainings"];

/** Search and filter across colleagues, documents and trainings. */
export function ResourcesPage({ onboarding }: ResourcesPageProps) {
  const { colleagues, documents, trainings } = onboarding;
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ResourceFilter>("All");

  const q = query.trim().toLowerCase();
  const matches = (...fields: string[]) => !q || fields.some((field) => field.toLowerCase().includes(q));
  const wants = (kind: ResourceFilter) => filter === "All" || filter === kind;

  const filteredColleagues = useMemo(
    () => (wants("People") ? colleagues.filter((c) => matches(c.name, c.role)) : []),
    [colleagues, filter, q],
  );
  const filteredDocuments = useMemo(
    () => (wants("Documents") ? documents.filter((d) => matches(d.title, d.format)) : []),
    [documents, filter, q],
  );
  const filteredTrainings = useMemo(
    () => (wants("Trainings") ? trainings.filter((t) => matches(t.title)) : []),
    [trainings, filter, q],
  );

  const resultCount = filteredColleagues.length + filteredDocuments.length + filteredTrainings.length;
  const resultsLabel =
    resultCount === 0
      ? "No results"
      : `${resultCount} ${resultCount === 1 ? "result" : "results"}${filter === "All" ? "" : ` in ${filter}`}`;

  function clearSearch() {
    setQuery("");
    setFilter("All");
  }

  return (
    <>
      <div className="bn-card" style={{ display: "flex", flexDirection: "column", gap: 14 }}>
        <label className="bn-field">
          <span className="bn-field__label">Search resources</span>
          <input
            type="search"
            className="bn-input"
            placeholder="Colleague, document or training"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <div role="group" aria-label="Filter by type" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {FILTERS.map((f) => (
            <button
              key={f}
              type="button"
              className="bn-filter-chip"
              aria-pressed={filter === f}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
        <div role="status" style={{ font: "400 13px/1.45 var(--bn-font)", color: "var(--bn-color-ink-subtle)" }}>
          {resultsLabel}
        </div>
      </div>

      <ColleaguesList colleagues={filteredColleagues} />
      <DocumentsList documents={filteredDocuments} />
      <TrainingList trainings={filteredTrainings} />

      {resultCount === 0 && (
        <div className="bn-card" style={{ padding: "30px 20px", display: "flex", flexDirection: "column", gap: 13, alignItems: "flex-start" }}>
          <div style={{ font: "700 16px/1.25 var(--bn-font)" }}>No resource matches "{query}"</div>
          <p style={{ margin: 0, font: "400 14px/1.6 var(--bn-font)", color: "var(--bn-color-ink-subtle)", maxWidth: "50ch" }}>
            Try a colleague's name, a document title, or clear the search to see everything in your template.
          </p>
          <button type="button" className="bn-button bn-button--secondary" onClick={clearSearch}>
            Clear search and filters
          </button>
        </div>
      )}
    </>
  );
}
