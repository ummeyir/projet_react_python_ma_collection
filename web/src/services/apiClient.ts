import type {
	ApiEntry,
	ApiItem,
	ApiItemList,
	ApiStats,
	ApiToken,
	ApiUser,
	AuthResponse,
	AuthUser,
	CollectionEntry,
	CollectionListResponse,
	CollectionQueryParams,
	CollectionStats,
	CreateCollectionEntryRequest,
	Item,
	ItemListResponse,
	LoginRequest,
	ParametresItems,
	RegisterRequest,
	UpdateCollectionEntryRequest,
} from "../types/api";

const API_BASE_URL = (
	import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

const ITEM_CATEGORIES = [
	"Abdominaux",
	"Bras",
	"Cardio",
	"Dos",
	"Full body",
	"Jambes",
	"Pectoraux",
	"Épaules",
];

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

function mapItem(item: ApiItem): Item {
	return {
		id: item.id,
		name: item.titre,
		category: item.categorie,
		description: item.description,
		image_url: item.image_url,
		muscle_group: item.groupe_musculaire,
		equipment: item.equipement,
		difficulty: item.difficulte,
	};
}

function mapEntry(entry: ApiEntry): CollectionEntry {
	return {
		id: entry.id,
		item_id: entry.item.id,
		status: entry.statut,
		rating: entry.note,
		comment: entry.commentaire,
		added_at: entry.date_ajout,
		item: mapItem(entry.item),
	};
}

function toApiEntryPayload(payload: CreateCollectionEntryRequest | UpdateCollectionEntryRequest) {
	return {
		...( "item_id" in payload ? { item_id: payload.item_id } : {}),
		...(payload.status !== undefined ? { statut: payload.status } : {}),
		...(payload.rating !== undefined ? { note: payload.rating } : {}),
		...(payload.comment !== undefined ? { commentaire: payload.comment } : {}),
	};
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
	const user = await requestJson<ApiUser>("/auth/register", {
		method: "POST",
		body: JSON.stringify(payload),
	});
	return user;
}

export async function loginUser(payload: LoginRequest): Promise<AuthResponse> {
	return requestJson<ApiToken>("/auth/login", {
		method: "POST",
		body: JSON.stringify(payload),
	});
}

export async function getCurrentUser(
	token: string,
	signal?: AbortSignal,
): Promise<AuthUser> {
	return requestJson<ApiUser>("/auth/me", {
		headers: { Authorization: `Bearer ${token}` },
		signal,
	});
}

export async function getCollection(
	token: string,
	parameters: CollectionQueryParams = {},
	signal?: AbortSignal,
): Promise<CollectionListResponse> {
	const searchParameters = new URLSearchParams();
	if (parameters.status) searchParameters.set("statut", parameters.status);
	if (parameters.sort) {
		searchParameters.set("tri", parameters.sort === "rating" ? "note" : "date");
	}
	const query = searchParameters.toString();
	const response = await requestJson<ApiEntry[]>(
		`/me/collection${query ? `?${query}` : ""}`,
		{ headers: { Authorization: `Bearer ${token}` }, signal },
	);
	const allEntries = response.map(mapEntry);
	const page = parameters.page ?? 1;
	const size = parameters.size ?? Math.max(1, allEntries.length);
	const start = (page - 1) * size;
	return {
		items: allEntries.slice(start, start + size),
		total: allEntries.length,
		page,
		size,
	};
}

export async function addCollectionEntry(
	token: string,
	payload: CreateCollectionEntryRequest,
): Promise<void> {
	await requestJson<unknown>("/me/collection", {
		method: "POST",
		headers: { Authorization: `Bearer ${token}` },
		body: JSON.stringify(toApiEntryPayload(payload)),
	});
}

export async function updateCollectionEntry(
	token: string,
	entryId: number,
	payload: UpdateCollectionEntryRequest,
): Promise<void> {
	await requestJson<unknown>(`/me/collection/${entryId}`, {
		method: "PATCH",
		headers: { Authorization: `Bearer ${token}` },
		body: JSON.stringify(toApiEntryPayload(payload)),
	});
}

export async function removeCollectionEntry(token: string, entryId: number): Promise<void> {
	await requestJson<unknown>(`/me/collection/${entryId}`, {
		method: "DELETE",
		headers: { Authorization: `Bearer ${token}` },
	});
}

export async function getCollectionStats(
	token: string,
	signal?: AbortSignal,
): Promise<CollectionStats> {
	const stats = await requestJson<ApiStats>("/me/stats", {
		headers: { Authorization: `Bearer ${token}` },
		signal,
	});
	return {
		total: stats.total,
		by_status: stats.par_statut,
		average_rating: stats.note_moyenne,
	};
}

export async function getItems(
	parameters: ParametresItems,
	signal?: AbortSignal,
): Promise<ItemListResponse> {
	const searchParameters = new URLSearchParams();
	if (parameters.q?.trim()) searchParameters.set("q", parameters.q.trim());
	if (parameters.category) searchParameters.set("categorie", parameters.category);
	if (parameters.page !== undefined) searchParameters.set("page", String(parameters.page));
	if (parameters.size !== undefined) searchParameters.set("limit", String(parameters.size));

	const query = searchParameters.toString();
	const response = await requestJson<ApiItemList>(
		`/items${query ? `?${query}` : ""}`,
		{ signal },
	);
	return {
		items: response.results.map(mapItem),
		total: response.total,
		page: response.page,
		size: response.limit,
		categories: ITEM_CATEGORIES,
	};
}

export async function getItem(itemId: number, signal?: AbortSignal): Promise<Item> {
	return mapItem(await requestJson<ApiItem>(`/items/${itemId}`, { signal }));
}