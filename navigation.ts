import type { ScreenId } from "../types";

export interface NavItem {
  screen: ScreenId;
  label: string;
  shortLabel: string;
  /** Count badge (e.g. remaining checklist steps), or `null` to hide it. */
  count: number | null;
}

/**
 * Builds the five primary navigation entries. `remainingSteps` drives the
 * badge on "My checklist", matching the reference prototype's `navDefs`.
 */
export function buildNavItems(remainingSteps: number): NavItem[] {
  return [
    { screen: "home", label: "Home", shortLabel: "Home", count: null },
    { screen: "checklist", label: "My checklist", shortLabel: "Checklist", count: remainingSteps },
    { screen: "resources", label: "Resources", shortLabel: "Resources", count: null },
    { screen: "signature", label: "Email signature", shortLabel: "Signature", count: null },
    { screen: "profile", label: "My profile", shortLabel: "Profile", count: null },
  ];
}
