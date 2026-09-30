export type CollectionStatus = "a_decouvrir" | "en_cours" | "termine";

export type CollectionSort = "date" | "rating";

export interface Item {
	id: number;
	name: string;
	category: string;
	description: string;
	image_url: string | null;
	muscle_group: string;
	equipment: string;
	difficulty: string;
}

export interface ItemListResponse {
	items: Item[];
	total: number;
	page: number;
	size: number;
	categories: string[];
}

export interface ParametresItems {
	q?: string;
	category?: string;
	difficulty?: string;
	page?: number;
	size?: number;
}

export interface AuthUser {
	id: number;
	username: string;
	email: string;
}

export interface RegisterRequest {
	username: string;
	email: string;
	password: string;
}

export interface LoginRequest {
	email: string;
	password: string;
}

export interface AuthResponse {
	access_token: string;
	token_type: "bearer";
	user: AuthUser;
}

export interface CollectionEntry {
	id: number;
	item_id: number;
	status: CollectionStatus;
	rating: number | null;
	comment: string | null;
	added_at: string;
	item: Item;
}

export interface CollectionListResponse {
	items: CollectionEntry[];
	total: number;
	page: number;
	size: number;
}

export interface CreateCollectionEntryRequest {
	item_id: number;
	status: CollectionStatus;
	rating?: number;
	comment?: string;
}

export interface UpdateCollectionEntryRequest {
	status?: CollectionStatus;
	rating?: number | null;
	comment?: string | null;
}

export interface CollectionQueryParams {
	status?: CollectionStatus;
	sort?: CollectionSort;
	page?: number;
	size?: number;
}

export interface CollectionStats {
	total: number;
	by_status: Record<CollectionStatus, number>;
	average_rating: number | null;
}

export interface ErreurApi {
	erreur: {
		code: number;
		message: string;
	};
}
