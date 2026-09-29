import type {
	AuthResponse,
	AuthUser,
	Item,
	ItemListResponse,
	LoginRequest,
	ParametresItems,
	RegisterRequest,
} from "../types/api";

const API_BASE_URL = (
	import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

export class ApiError extends Error {
	readonly status: number;

	constructor(message: string, status: number) {
		super(message);
		this.name = "ApiError";
		this.status = status;
	}
}

function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null;
}

function getApiErrorMessage(payload: unknown, status: number): string {
	if (isRecord(payload) && isRecord(payload.erreur)) {
		const message = payload.erreur.message;
		if (typeof message === "string") {
			return message;
		}
	}

	return `La requête a échoué (HTTP ${status}).`;
}

async function requestJson<T>(path: string, options: RequestInit = {}): Promise<T> {
	const headers = new Headers(options.headers);
	headers.set("Accept", "application/json");
	if (options.body !== undefined) {
		headers.set("Content-Type", "application/json");
	}

	const response = await fetch(`${API_BASE_URL}${path}`, {
		...options,
		headers,
	});
	const payload: unknown = await response.json().catch(() => null);

	if (!response.ok) {
		throw new ApiError(getApiErrorMessage(payload, response.status), response.status);
	}

	return payload as T;
}

export async function registerUser(payload: RegisterRequest): Promise<AuthUser> {
	return requestJson<AuthUser>("/auth/register", {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export async function loginUser(payload: LoginRequest): Promise<AuthResponse> {
	return requestJson<AuthResponse>("/auth/login", {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export async function getCurrentUser(
	token: string,
	signal?: AbortSignal,
): Promise<AuthUser> {
	return requestJson<AuthUser>("/auth/me", {
		headers: { Authorization: `Bearer ${token}` },
		signal,
	});
}

export async function getItems(
	parameters: ParametresItems,
	signal?: AbortSignal,
): Promise<ItemListResponse> {
	const searchParameters = new URLSearchParams();
	for (const [key, value] of Object.entries(parameters)) {
		if (value !== undefined && String(value).trim() !== "") {
			searchParameters.set(key, String(value));
		}
	}

	const query = searchParameters.toString();
	return requestJson<ItemListResponse>(
		`/items${query ? `?${query}` : ""}`,
		{ signal },
	);
}

export async function getItem(itemId: number, signal?: AbortSignal): Promise<Item> {
	return requestJson<Item>(`/items/${itemId}`, { signal });
}