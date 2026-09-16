import { useCallback, useMemo, useState } from "react";
import {
  DEV_AGENTS,
  SEED_COLLEAGUES,
  SEED_DOCUMENTS,
  SEED_PROFILE,
  SEED_TEMPLATE,
  SEED_TODOS,
  SEED_TRAININGS,
} from "../data/seed";
import { buildSignatureText, computeTodoStatuses, findCurrentStep } from "../lib/onboarding";
import type { AgentProfile, ScreenId, TodoWithStatus } from "../types";
import { useAlert } from "./useAlert";
import { useLocalStorageState } from "./useLocalStorageState";

const STORAGE_KEY = "bienvenue.app.v1";
const LOGIN_DELAY_MS = 900;
const VERIFY_DELAY_MS = 1100;
const ACCEPT_SIGNATURE_DELAY_MS = 800;

interface PersistedSession {
  email: string | null;
  screen: ScreenId;
  done: Record<string, boolean>;
  doneAt: Record<string, string>;
  signatureAccepted: boolean;
  profile: AgentProfile;
}

const INITIAL_SESSION: PersistedSession = {
  email: null,
  screen: "home",
  done: {},
  doneAt: {},
  signatureAccepted: false,
  profile: { ...SEED_PROFILE },
};

/**
 * Simulates `GET /api/mock-suite/fichiers/users/{email}/` (see
 * `05-local-development.md`, section 6.1). Fixed to a successful lookup
 * here; swap for a real API call once the Django BFF is reachable from the
 * frontend, keeping this same async shape so callers do not need to change.
 */
async function checkFichiersAccount(_email: string): Promise<{ exists: boolean }> {
  await new Promise((resolve) => setTimeout(resolve, VERIFY_DELAY_MS));
  return { exists: true };
}

/**
 * Loads and mutates the New Agent's onboarding state.
 *
 * This is the local-prototype stand-in for the `useOnboarding.ts` /
 * `useManager.ts` TanStack Query hooks described in `03-frontend-app.md`.
 * It persists to `localStorage` under {@link STORAGE_KEY} instead of
 * calling `GET /api/onboarding/me/`, `POST /api/todos/{id}/verify/`, etc.,
 * but exposes the same conceptual actions so pages don't need to change
 * when the real BFF is wired up.
 */
export function useOnboarding() {
  const [session, setSession] = useLocalStorageState<PersistedSession>(STORAGE_KEY, INITIAL_SESSION);
  const [devEmail, setDevEmail] = useState<string>("alex.martin@gouv.fr");
  const [loggingIn, setLoggingIn] = useState(false);
  const [busyTodoId, setBusyTodoId] = useState<string | null>(null);
  const [acceptingSignature, setAcceptingSignature] = useState(false);
  const { alert, flash, dismiss } = useAlert();

  const agentMeta = session.email ? DEV_AGENTS[session.email] : undefined;
  const agent = { name: session.profile.name || agentMeta?.name || "", email: session.email ?? "" };

  const todos: TodoWithStatus[] = useMemo(
    () => computeTodoStatuses(SEED_TODOS, session.done, session.doneAt, session.signatureAccepted),
    [session.done, session.doneAt, session.signatureAccepted],
  );
  const currentStep = findCurrentStep(todos);
  const doneCount = todos.filter((t) => t.done).length;

  const signIn = useCallback(() => {
    if (loggingIn) return;
    setLoggingIn(true);
    setTimeout(() => {
      const meta = DEV_AGENTS[devEmail];
      const seededDone = { ...meta.seedDone };
      const seededDoneAt: Record<string, string> = seededDone.t1
        ? { t1: new Date(Date.now() - 3_600_000).toISOString() }
        : {};
      setLoggingIn(false);
      setSession({
        email: devEmail,
        screen: "home",
        done: seededDone,
        doneAt: seededDoneAt,
        signatureAccepted: false,
        profile: { ...SEED_PROFILE },
      });
    }, LOGIN_DELAY_MS);
  }, [devEmail, loggingIn, setSession]);

  const signOut = useCallback(() => {
    setSession((previous) => ({ ...previous, email: null, screen: "home" }));
    dismiss();
  }, [dismiss, setSession]);

  const goToScreen = useCallback(
    (screen: ScreenId) => setSession((previous) => ({ ...previous, screen })),
    [setSession],
  );

  /** Runs the `API_CHECK` verification flow for a single checklist step. */
  const verifyTodo = useCallback(
    async (todoId: string) => {
      if (busyTodoId) return;
      setBusyTodoId(todoId);
      const todo = todos.find((t) => t.id === todoId);
      const result = await checkFichiersAccount(agent.email);
      setBusyTodoId(null);

      if (result.exists) {
        setSession((previous) => ({
          ...previous,
          done: { ...previous.done, [todoId]: true },
          doneAt: { ...previous.doneAt, [todoId]: new Date().toISOString() },
        }));
        flash(
          "success",
          "Fichiers account verified",
          `The service returned HTTP 200 for ${agent.email}. Step ${(todo?.order ?? 0) + 1} is now unlocked.`,
        );
      } else {
        flash(
          "error",
          "Account not found in Fichiers",
          "The service returned HTTP 404. Your storage space has not been provisioned yet — activate it, then verify again.",
        );
      }
    },
    [agent.email, busyTodoId, flash, setSession, todos],
  );

  /** Toggles a `MANUAL` checklist step on or off (the "honor system" from `00-architecture-overview.md`). */
  const toggleTodo = useCallback(
    (todoId: string, nextDone: boolean) => {
      const label = todos.find((t) => t.id === todoId)?.label ?? "";
      setSession((previous) => {
        const done = { ...previous.done };
        const doneAt = { ...previous.doneAt };
        if (nextDone) {
          done[todoId] = true;
          doneAt[todoId] = new Date().toISOString();
        } else {
          delete done[todoId];
          delete doneAt[todoId];
        }
        return { ...previous, done, doneAt };
      });
      flash(
        nextDone ? "success" : "info",
        nextDone ? "Step marked as done" : "Step reopened",
        nextDone
          ? `Self-declared completion recorded for "${label}".`
          : `"${label}" is open again. Later steps are locked until it is resolved.`,
      );
    },
    [flash, setSession, todos],
  );

  const acceptSignature = useCallback(() => {
    if (acceptingSignature) return;
    setAcceptingSignature(true);
    setTimeout(() => {
      setAcceptingSignature(false);
      setSession((previous) => ({ ...previous, signatureAccepted: true }));
      flash("success", "Signature confirmed", "POST /api/signature/accept/ returned 200. Your onboarding checklist is now complete.");
    }, ACCEPT_SIGNATURE_DELAY_MS);
  }, [acceptingSignature, flash, setSession]);

  const saveProfile = useCallback(
    (profile: AgentProfile) => {
      setSession((previous) => ({ ...previous, profile }));
      flash("success", "Details saved", "Your signature has been regenerated from the updated values.");
    },
    [flash, setSession],
  );

  const resetAll = useCallback(() => {
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // Ignore — state below still resets the in-memory session.
    }
    setSession(INITIAL_SESSION);
    dismiss();
  }, [dismiss, setSession]);

  const signatureText = buildSignatureText(agent, session.profile);

  return {
    isAuthenticated: !!session.email,
    agent,
    devEmail,
    setDevEmail,
    loggingIn,
    signIn,
    signOut,

    screen: session.screen,
    goToScreen,

    template: SEED_TEMPLATE,
    todos,
    currentStep,
    doneCount,
    totalCount: todos.length,
    busyTodoId,
    verifyTodo,
    toggleTodo,

    colleagues: SEED_COLLEAGUES,
    documents: SEED_DOCUMENTS,
    trainings: SEED_TRAININGS,

    profile: session.profile,
    saveProfile,

    signatureAccepted: session.signatureAccepted,
    signatureText,
    acceptingSignature,
    acceptSignature,

    alert,
    dismissAlert: dismiss,
    resetAll,
  };
}

export type UseOnboardingReturn = ReturnType<typeof useOnboarding>;
