import { useCallback, useEffect, useRef, useState } from "react";
import type { AlertKind, AlertState } from "../types";

const AUTO_DISMISS_MS = 7000;

/** Manages the single transient alert banner shown below the app header. */
export function useAlert() {
  const [alert, setAlert] = useState<AlertState | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const flash = useCallback((kind: AlertKind, title: string, body: string) => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setAlert({ kind, title, body });
    timerRef.current = setTimeout(() => setAlert(null), AUTO_DISMISS_MS);
  }, []);

  const dismiss = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    setAlert(null);
  }, []);

  useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current);
  }, []);

  return { alert, flash, dismiss };
}
