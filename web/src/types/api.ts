export type Statut = "a_decouvrir" | "en_cours" | "termine";

export type TriCollection = "date" | "note";

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

export interface Utilisateur {
	id: number;
	email: string;
}

export interface InscriptionRequest {
	email: string;
	password: string;
}

export interface ConnexionRequest {
	email: string;
	password: string;
}

export interface TokenResponse {
	access_token: string;
	token_type: "bearer";
}

export interface EntreeCollection {
	id: number;
	statut: Statut;
	note: number | null;
	commentaire: string | null;
	date_ajout: string;
	item: Item;
}

export interface AjouterCollectionRequest {
	item_id: number;
	statut: Statut;
	note?: number;
	commentaire?: string;
}

export interface ModifierCollectionRequest {
	statut?: Statut;
	note?: number | null;
	commentaire?: string | null;
}

export interface ParametresCollection {
	statut?: Statut;
	tri?: TriCollection;
}

export interface StatistiquesCollection {
	total: number;
	par_statut: Record<Statut, number>;
	note_moyenne: number | null;
}

export interface ErreurApi {
	erreur: {
		code: number;
		message: string;
	};
}
