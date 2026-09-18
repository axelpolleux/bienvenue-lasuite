/**
 * Date formatting helpers for Bienvenue à La Suite.
 * Uses Europe/Paris timezone by default to align with official French civil service time.
 */

const DEFAULT_TIMEZONE = "Europe/Paris";

/** Formats an ISO timestamp as full date, e.g. "17 September 2026". */
export function formatFrenchDate(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
    timeZone: options?.timeZone || DEFAULT_TIMEZONE,
  }).format(date);
}

/** Formats an ISO timestamp as short date, e.g. "17 Sep 2026". */
export function formatFrenchDateShort(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  return new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: options?.timeZone || DEFAULT_TIMEZONE,
  }).format(date);
}

/** Formats an ISO timestamp as short date + time, e.g. "17 Sep at 15:30". */
export function formatFrenchDateTime(
  iso: string | null | undefined,
  options?: { timeZone?: string }
): string {
  if (!iso) return "";
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "";

  const timeZone = options?.timeZone || DEFAULT_TIMEZONE;
  const day = new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    timeZone,
  }).format(date);

  const time = new Intl.DateTimeFormat("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone,
  }).format(date);

  return `${day} at ${time}`;
}
