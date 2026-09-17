import type { HomeActivity } from "../../types";

const ICON_PROPS = {
  width: 18,
  height: 18,
  viewBox: "0 0 18 18",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

/** Pictogram for one Home "first days" activity tile. */
export function ActivityIcon({ icon }: { icon: HomeActivity["icon"] }) {
  switch (icon) {
    case "breakfast":
      return (
        <svg {...ICON_PROPS}>
          <path d="M4 8h8v3a4 4 0 0 1-4 4 4 4 0 0 1-4-4V8Z" />
          <path d="M12 9h1.3a2 2 0 0 1 0 4H12" />
          <path d="M6 8V6M9 8V5.3M11.5 8 11 6" />
        </svg>
      );
    case "meeting":
      return (
        <svg {...ICON_PROPS}>
          <circle cx="6.5" cy="7" r="2" />
          <circle cx="12" cy="7" r="2" />
          <path d="M2.7 14.3c.5-1.9 2-3 3.8-3s3.3 1.1 3.8 3" />
          <path d="M9.2 11.4c1.6.2 2.8 1.3 3.3 2.9" />
        </svg>
      );
    case "equipment":
      return (
        <svg {...ICON_PROPS}>
          <rect x="2.8" y="3.5" width="12.4" height="8.2" rx="1.2" />
          <path d="M6.5 15h5M9 11.7V15" />
        </svg>
      );
    case "tour":
      return (
        <svg {...ICON_PROPS}>
          <path d="M9 15.2S13.5 10.8 13.5 7a4.5 4.5 0 1 0-9 0c0 3.8 4.5 8.2 4.5 8.2Z" />
          <circle cx="9" cy="7" r="1.6" />
        </svg>
      );
    default:
      return null;
  }
}
