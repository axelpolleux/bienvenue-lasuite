import { useMemo, useState } from "react";
import { ColleaguesList } from "../components/onboarding/ColleaguesList";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";
import type { ContactFilter } from "../types";

export interface ContactPageProps {
  onboarding: UseOnboardingReturn;
}

const FILTERS: ContactFilter[] = ["All", "My team"];

/** People to reach on Tchap, moved out of Resources into its own tab. */
export function ContactPage({ onboarding }: ContactPageProps) {
  const { colleagues } = onboarding;
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<ContactFilter>("All");

  const q = query.trim().toLowerCase();
  const filteredColleagues = useMemo(
    () =>
      colleagues
        .filter((c) => filter === "All" || c.team)
        .filter((c) => !q || c.name.toLowerCase().includes(q) || c.role.toLowerCase().includes(q))
        .sort((a, b) => a.name.localeCompare(b.name)),
    [colleagues, filter, q],
  );

  return (
    <>
      <div className="bn-search-panel">
        <label className="bn-field">
          <span className="bn-field__label">Search colleagues</span>
          <input
            type="search"
            className="bn-input"
            placeholder="Name or role"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
      </div>

      <div className="bn-card" role="group" aria-label="Filter by team" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
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

      <ColleaguesList colleagues={filteredColleagues} />
    </>
  );
}
