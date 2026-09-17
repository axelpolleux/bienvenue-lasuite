import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { DEV_AGENTS, SEED_PROFILE } from "../data/seed";
import {
	acceptSignatureTask,
	fetchOnboardingBundle,
	toggleTodoTask,
	verifyTodoTask,
} from "../lib/api";
import { pullGrist, pushGrist } from "../lib/manager";
import { buildSignatureText, findCurrentStep } from "../lib/onboarding";
import type {
	Agent,
	AgentProfile,
	Colleague,
	OnboardingDocument,
	ScreenId,
	Template,
	TodoWithStatus,
	Training,
} from "../types";
import { useAlert } from "./useAlert";
import { useLocalStorageState } from "./useLocalStorageState";

const STORAGE_KEY = "bienvenue.app.v1";

interface PersistedSession {
	activeDevEmail: string | null;
	screen: ScreenId;
	email?: string | null;
}

const INITIAL_SESSION: PersistedSession = {
	activeDevEmail: null,
	screen: "home",
};

interface TodoMutationsParams {
	activeDevEmail: string | null;
	todos: TodoWithStatus[];
	agentEmail: string;
	flash: (kind: "success" | "error" | "info", title: string, body: string) => void;
}

/**
 * Handles API verification and manual status mutations for checklist items.
 */
function useTodoMutations({ activeDevEmail, todos, agentEmail, flash }: TodoMutationsParams) {
	const queryClient = useQueryClient();

	const verifyMutation = useMutation({
		mutationFn: (todoId: string) => verifyTodoTask(todoId, activeDevEmail || undefined),
		onSuccess: (_data, todoId) => {
			queryClient.invalidateQueries({ queryKey: ["onboarding", activeDevEmail] });
			const todo = todos.find((t) => t.id === todoId);
			const name = todo?.serviceName || "Service";
			flash("success", `${name} account verified`, `The service confirmed access for ${agentEmail}.`);
		},
		onError: (error) => {
			const detail = error instanceof Error ? error.message : "The service could not verify your account.";
			flash("error", "Verification failed", detail);
		},
	});

	const toggleMutation = useMutation({
		mutationFn: ({ todoId, nextDone }: { todoId: string; nextDone: boolean }) =>
			toggleTodoTask(todoId, nextDone, activeDevEmail || undefined),
		onSuccess: (_data, { todoId, nextDone }) => {
			queryClient.invalidateQueries({ queryKey: ["onboarding", activeDevEmail] });
			const label = todos.find((t) => t.id === todoId)?.label ?? "";
			flash(
				nextDone ? "success" : "info",
				nextDone ? "Step marked as done" : "Step reopened",
				nextDone
					? `Self-declared completion recorded for "${label}".`
					: `"${label}" is open again. Later steps are locked until it is resolved.`,
			);
		},
		onError: (error) => {
			const detail = error instanceof Error ? error.message : "Could not update task status.";
			flash("error", "Failed to update task", detail);
		},
	});

	const verifyTodo = useCallback(
		(todoId: string) => {
			if (!verifyMutation.isPending) verifyMutation.mutate(todoId);
		},
		[verifyMutation],
	);

	const toggleTodo = useCallback(
		(todoId: string, nextDone: boolean) => {
			if (!toggleMutation.isPending) toggleMutation.mutate({ todoId, nextDone });
		},
		[toggleMutation],
	);

	const busyTodoId = verifyMutation.isPending ? (verifyMutation.variables as string) ?? null : null;

	return { busyTodoId, verifyTodo, toggleTodo };
}

interface SignatureMutationParams {
	activeDevEmail: string | null;
	flash: (kind: "success" | "error" | "info", title: string, body: string) => void;
}

/**
 * Handles official email signature validation mutation.
 */
function useSignatureMutation({ activeDevEmail, flash }: SignatureMutationParams) {
	const queryClient = useQueryClient();

	const mutation = useMutation({
		mutationFn: () => acceptSignatureTask(activeDevEmail || undefined),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["onboarding", activeDevEmail] });
			flash("success", "Signature confirmed", "POST /api/signature/accept/ returned 200. Your onboarding checklist is now complete.");
		},
		onError: (error) => {
			const detail = error instanceof Error ? error.message : "Could not confirm signature setup.";
			flash("error", "Failed to confirm signature", detail);
		},
	});

	const acceptSignature = useCallback(() => {
		if (!mutation.isPending) mutation.mutate();
	}, [mutation]);

	return {
		acceptingSignature: mutation.isPending,
		acceptSignature,
	};
}

interface ManagerGristSyncParams {
	activeDevEmail: string | null;
	flash: (kind: "success" | "error" | "info", title: string, body: string) => void;
}

/**
 * Handles on-demand bidirectional Grist synchronization mutations.
 */
function useManagerGristSync({ activeDevEmail, flash }: ManagerGristSyncParams) {
	const queryClient = useQueryClient();

	const pullMutation = useMutation({
		mutationFn: () => pullGrist(activeDevEmail || undefined),
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: ["onboarding"] });
			const count = Object.values(data.synced || {}).reduce((acc, v) => acc + v, 0);
			flash(
				"success",
				"Grist sync successful",
				`Data fetched from Grist successfully (${count} items updated).`,
			);
		},
		onError: (error) => {
			const detail = error instanceof Error ? error.message : "Could not connect to Grist.";
			flash("error", "Sync failed", detail);
		},
	});

	const pushMutation = useMutation({
		mutationFn: () => pushGrist(activeDevEmail || undefined),
		onSuccess: (data) => {
			const { updated = 0, created = 0 } = data.results || {};
			flash(
				"success",
				"Progress pushed to Grist",
				`Progress synced successfully (${updated + created} tasks updated in Grist).`,
			);
		},
		onError: (error) => {
			const detail = error instanceof Error ? error.message : "Could not connect to Grist.";
			flash("error", "Push failed", detail);
		},
	});

	const pullGristSync = useCallback(() => {
		if (!pullMutation.isPending && !pushMutation.isPending) {
			pullMutation.mutate();
		}
	}, [pullMutation, pushMutation]);

	const pushGristSync = useCallback(() => {
		if (!pullMutation.isPending && !pushMutation.isPending) {
			pushMutation.mutate();
		}
	}, [pullMutation, pushMutation]);

	return {
		pullGristSync,
		pushGristSync,
		isPullingGrist: pullMutation.isPending,
		isPushingGrist: pushMutation.isPending,
		isSyncingGrist: pullMutation.isPending || pushMutation.isPending,
	};
}

interface UseOnboardingAuthParams {
	queryClient: ReturnType<typeof useQueryClient>;
	dismissAlert: () => void;
	flash: (kind: "success" | "error" | "info", title: string, body: string) => void;
}

/**
 * Manages persisted session, dev bypass identities, and sign-in/out routing.
 */
function useOnboardingAuth({ queryClient, dismissAlert, flash }: UseOnboardingAuthParams) {
	const [session, setSession] = useLocalStorageState<PersistedSession>(STORAGE_KEY, INITIAL_SESSION);
	const activeDevEmail = session.activeDevEmail ?? session.email ?? null;
	const [devEmail, setDevEmail] = useState<string>("alex.martin@gouv.fr");
	const [loggingIn, setLoggingIn] = useState(false);

	const signInKeycloak = useCallback(() => {
		window.location.href = "/oidc/authenticate/";
	}, []);

	const signInDev = useCallback(
		async (email?: string) => {
			const target = email || devEmail;
			setLoggingIn(true);
			try {
				await queryClient.fetchQuery({
					queryKey: ["onboarding", target],
					queryFn: () => fetchOnboardingBundle(target),
				});
				setSession({ activeDevEmail: target, screen: "home" });
				dismissAlert();
			} catch (err) {
				const msg = err instanceof Error ? err.message : "Failed to sign in.";
				flash("error", "Dev Sign In Failed", msg);
			} finally {
				setLoggingIn(false);
			}
		},
		[devEmail, dismissAlert, flash, queryClient, setSession],
	);

	const signOut = useCallback(() => {
		const hadDev = Boolean(activeDevEmail);
		setSession({ activeDevEmail: null, screen: "home" });
		queryClient.clear();
		dismissAlert();
		if (!hadDev) {
			window.location.href = "/oidc/logout/";
		}
	}, [activeDevEmail, dismissAlert, queryClient, setSession]);

	const goToScreen = useCallback(
		(screen: ScreenId) => setSession((prev) => ({ ...prev, screen })),
		[setSession],
	);

	const resetAll = useCallback(() => {
		try {
			window.localStorage.removeItem(STORAGE_KEY);
		} catch {
			// Storage unavailable
		}
		setSession(INITIAL_SESSION);
		queryClient.clear();
		dismissAlert();
	}, [dismissAlert, queryClient, setSession]);

	return {
		session,
		activeDevEmail,
		devEmail,
		setDevEmail,
		loggingIn,
		signInDev,
		signInKeycloak,
		signOut,
		goToScreen,
		resetAll,
	};
}

/**
 * Loads and mutates the New Agent's onboarding state via TanStack Query.
 */
export function useOnboarding() {
	const queryClient = useQueryClient();
	const { alert, flash, dismiss } = useAlert();
	const auth = useOnboardingAuth({ queryClient, dismissAlert: dismiss, flash });
	const { activeDevEmail } = auth;
	const [profile] = useState<AgentProfile>({ ...SEED_PROFILE });

	const query = useQuery({
		queryKey: ["onboarding", activeDevEmail],
		queryFn: () => fetchOnboardingBundle(activeDevEmail || undefined),
		retry: false,
	});

	const agent: Agent = useMemo(() => {
		if (query.data?.agent) return query.data.agent;
		const meta = activeDevEmail ? DEV_AGENTS[activeDevEmail] : undefined;
		return { name: meta?.name || "", email: activeDevEmail ?? "" };
	}, [query.data?.agent, activeDevEmail]);

	const template: Template | null = query.data?.template ?? null;
	const todos: TodoWithStatus[] = useMemo(() => query.data?.todos ?? [], [query.data?.todos]);
	const colleagues: Colleague[] = useMemo(() => query.data?.colleagues ?? [], [query.data?.colleagues]);
	const documents: OnboardingDocument[] = useMemo(() => query.data?.documents ?? [], [query.data?.documents]);
	const trainings: Training[] = useMemo(() => query.data?.trainings ?? [], [query.data?.trainings]);

	const currentStep = findCurrentStep(todos);
	const doneCount = todos.filter((t) => t.done).length;
	const signatureAccepted = Boolean(query.data?.agent.signatureAccepted);
	const signatureText = buildSignatureText(agent, profile);

	const { busyTodoId, verifyTodo, toggleTodo } = useTodoMutations({
		activeDevEmail,
		todos,
		agentEmail: agent.email,
		flash,
	});

	const { acceptingSignature, acceptSignature } = useSignatureMutation({
		activeDevEmail,
		flash,
	});

	const {
		pullGristSync,
		pushGristSync,
		isPullingGrist,
		isPushingGrist,
		isSyncingGrist,
	} = useManagerGristSync({
		activeDevEmail,
		flash,
	});

	return {
		isAuthenticated: !query.isError && !!query.data,
		isLoadingInitial: query.isLoading,
		agent,
		devEmail: auth.devEmail,
		setDevEmail: auth.setDevEmail,
		loggingIn: auth.loggingIn,
		signIn: () => auth.signInDev(auth.devEmail),
		signInDev: auth.signInDev,
		signInKeycloak: auth.signInKeycloak,
		signOut: auth.signOut,
		screen: auth.session.screen,
		goToScreen: auth.goToScreen,
		template,
		todos,
		currentStep,
		doneCount,
		totalCount: todos.length,
		busyTodoId,
		verifyTodo,
		toggleTodo,
		colleagues,
		documents,
		trainings,
		profile,
		signatureAccepted,
		signatureText,
		acceptingSignature,
		acceptSignature,
		pullGristSync,
		pushGristSync,
		isPullingGrist,
		isPushingGrist,
		isSyncingGrist,
		alert,
		dismissAlert: dismiss,
		resetAll: auth.resetAll,
	};
}

export type UseOnboardingReturn = ReturnType<typeof useOnboarding>;

