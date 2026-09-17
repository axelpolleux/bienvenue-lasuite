import { apiFetch } from "./api";

export interface SyncPullResponse {
	message: string;
	synced: Record<string, number>;
}

export interface SyncPushResponse {
	message: string;
	results: {
		updated: number;
		created: number;
		members_affected: number;
	};
}

/**
 * Pulls master onboarding data from Grist tables into PostgreSQL.
 */
export async function pullGrist(devEmail?: string): Promise<SyncPullResponse> {
	return apiFetch<SyncPullResponse>("/api/manager/sync-grist/pull/", {
		method: "POST",
		devEmail,
	});
}

/**
 * Pushes completed agent tasks from PostgreSQL into Grist MemberChecklist table.
 */
export async function pushGrist(devEmail?: string): Promise<SyncPushResponse> {
	return apiFetch<SyncPushResponse>("/api/manager/sync-grist/push/", {
		method: "POST",
		devEmail,
	});
}
