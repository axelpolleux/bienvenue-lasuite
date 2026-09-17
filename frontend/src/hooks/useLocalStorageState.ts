import { useCallback, useState } from "react";

/**
 * A `useState` drop-in that mirrors its value to `localStorage`.
 *
 * Used by {@link useOnboarding} in place of the reference prototype's
 * manual `localStorage.setItem` calls in `persist()`. When the real Django
 * BFF is wired up, this hook can be swapped for TanStack Query's cache
 * without changing any component that consumes {@link useOnboarding}.
 *
 * @param key - The localStorage key.
 * @param initialValue - Value used when nothing is stored yet, or storage is unavailable.
 */
export function useLocalStorageState<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => readStoredValue(key, initialValue));

  const setPersistedValue = useCallback(
    (next: T | ((previous: T) => T)) => {
      setValue((previous) => {
        const resolved = typeof next === "function" ? (next as (previous: T) => T)(previous) : next;
        writeStoredValue(key, resolved);
        return resolved;
      });
    },
    [key],
  );

  return [value, setPersistedValue] as const;
}

function readStoredValue<T>(key: string, fallback: T): T {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    // Storage may be unavailable (private browsing, disabled cookies, etc.).
    return fallback;
  }
}

function writeStoredValue<T>(key: string, value: T): void {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Non-fatal: the session simply won't survive a reload.
  }
}
