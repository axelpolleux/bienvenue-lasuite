/**
 * Date formatting helpers localized in French ('fr-FR') for Bienvenue à La Suite.
 * Uses Europe/Paris timezone by default to align with official French civil service time.
 */

const DEFAULT_TIMEZONE = "Europe/Paris";

/** Formats an ISO timestamp as full French date, e.g. "17 septembre 2026". */
export function formatFrenchDate(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("fr-FR", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: options?.timeZone || DEFAULT_TIMEZONE,
  }).format(date);
}

/** Formats an ISO timestamp as short French date, e.g. "17 sept. 2026". */
export function formatFrenchDateShort(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("fr-FR", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: options?.timeZone || DEFAULT_TIMEZONE,
  }).format(date);
}

/** Formats an ISO timestamp as short date + time in French, e.g. "17 sept. à 15:30". */
export function formatFrenchDateTime(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  const timeZone = options?.timeZone || DEFAULT_TIMEZONE;
  const day = new Intl.DateTimeFormat("fr-FR", {
    day: "numeric",
    month: "short",
    timeZone,
  }).format(date);

  const time = new Intl.DateTimeFormat("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone,
  }).format(date);

  return `${day} à ${time}`;
}
