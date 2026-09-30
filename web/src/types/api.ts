export type CollectionStatus = "a_decouvrir" | "en_cours" | "termine";

export type CollectionSort = "date" | "rating";

export type ApiCollectionSort = "date" | "note";

export interface ApiItem {
	id: number;
	titre: string;
	categorie: string;
	description: string;
	image_url: string | null;
	annee: number | null;
	groupe_musculaire: string;
	equipement: string;
	difficulte: string;
}

export interface ApiItemList {
	total: number;
	page: number;
	limit: number;
	results: ApiItem[];
}

export interface ApiEntry {
	id: number;
	statut: CollectionStatus;
	note: number | null;
	commentaire: string | null;
	date_ajout: string;
	item: ApiItem;
}

export interface ApiStats {
	total: number;
	par_statut: Record<CollectionStatus, number>;
	note_moyenne: number | null;
}

export interface ApiUser {
	id: number;
	email: string;
}

export interface ApiToken {
	access_token: string;
	token_type: "bearer";
}

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
	email: string;
}

export interface RegisterRequest {
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
