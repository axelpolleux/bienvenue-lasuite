import type { ScreenId } from "../../types";

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

/** Thin-stroke, single-colour pictogram for each primary nav entry (replaces the plain square dot). */
export function NavIcon({ screen }: { screen: ScreenId }) {
  switch (screen) {
    case "home":
      return (
        <svg {...ICON_PROPS}>
          <path d="M2.5 8.7 9 3.2l6.5 5.5" />
          <path d="M4.2 7.6V15h9.6V7.6" />
          <path d="M7.2 15v-4.6h3.6V15" />
        </svg>
      );
    case "checklist":
      return (
        <svg {...ICON_PROPS}>
          <rect x="3" y="3" width="12" height="12" rx="2" />
          <path d="M5.8 9.1 7.6 11l4-4.6" />
        </svg>
      );
    case "contact":
      return (
        <svg {...ICON_PROPS}>
          <rect x="4" y="2.5" width="10" height="13" rx="1.5" />
          <circle cx="9" cy="7" r="1.6" />
          <path d="M6.3 12c.5-1.3 1.6-2 2.7-2s2.2.7 2.7 2" />
        </svg>
      );
    case "resources":
      return (
        <svg {...ICON_PROPS}>
          <path d="M3 4.2c1.7-.8 3.5-.8 5.2 0v10c-1.7-.8-3.5-.8-5.2 0v-10Z" />
          <path d="M15 4.2c-1.7-.8-3.5-.8-5.2 0v10c1.7-.8 3.5-.8 5.2 0v-10Z" />
        </svg>
      );
    case "signature":
      return (
        <svg {...ICON_PROPS}>
          <path d="M3.2 14.8c3-.7 4.2-8.6 7-10.7 1-.8 2.4.3 1.9 1.6-.9 2.4-3.7 4-6.2 4.4" />
          <path d="M11.9 4.1 14 6.1" />
          <path d="M3.2 14.8h11.6" />
        </svg>
      );
    default:
      return null;
  }
}
