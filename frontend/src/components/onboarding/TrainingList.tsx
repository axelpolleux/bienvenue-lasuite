import type { Training } from "../../types";

export interface TrainingListProps {
  trainings: Training[];
}

/** Curated training videos for the new agent. */
export function TrainingList({ trainings }: TrainingListProps) {
  if (trainings.length === 0) return null;

  return (
    <section style={{ display: "flex", flexDirection: "column", gap: 11 }}>
      <h3 style={{ margin: 0, font: "700 16px/1.2 var(--bn-font)" }}>Trainings</h3>
      {trainings.map((training) => (
        <div key={training.id} className="bn-resource-row">
          <span
            aria-hidden="true"
            style={{ width: 44, height: 44, borderRadius: 5, flex: "none", background: "#fceeac", display: "flex", alignItems: "center", justifyContent: "center" }}
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="#161616">
              <path d="M5 3.5 14.5 9 5 14.5z" />
            </svg>
          </span>
          <div className="bn-resource-row__body">
            <div className="bn-resource-row__title">{training.title}</div>
            <div className="bn-resource-row__subtitle">{training.durationMinutes} min video</div>
          </div>
          <a href={training.videoUrl} target="_blank" rel="noopener noreferrer" className="bn-button bn-button--link">
            Watch ↗
          </a>
        </div>
      ))}
    </section>
  );
}
