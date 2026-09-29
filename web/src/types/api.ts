export type Statut = "a_decouvrir" | "en_cours" | "termine";

export type TriCollection = "date" | "note";

export interface Item {
	id: number;
	titre: string;
	categorie: string;
	description: string;
	image_url: string;
	annee: number;
	groupe_musculaire: string;
	equipement: string;
}

export interface ListeItems {
	total: number;
	page: number;
	limit: number;
	results: Item[];
}

export interface ParametresItems {
	q?: string;
	categorie?: string;
	page?: number;
	limit?: number;
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
