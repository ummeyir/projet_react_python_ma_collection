import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
	addCollectionEntry,
	ApiError,
	getCollection,
	getItems,
	loginUser,
	registerUser,
	updateCollectionEntry,
} from "./apiClient";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(payload: unknown, status = 200): Response {
	return new Response(JSON.stringify(payload), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

beforeEach(() => {
	fetchMock.mockReset();
	vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
	vi.unstubAllGlobals();
});

describe("API client", () => {
	it("sends collection filters and the bearer token", async () => {
		fetchMock.mockResolvedValue(jsonResponse([{
			id: 9,
			statut: "en_cours",
			note: 4,
			commentaire: "Progression",
			date_ajout: "2026-01-01T00:00:00Z",
			item: {
				id: 4,
				titre: "Squat",
				categorie: "Jambes",
				description: "Exercice de jambes.",
				image_url: null,
				annee: null,
				groupe_musculaire: "Jambes",
				equipement: "Barre",
				difficulte: "Intermédiaire",
			},
		}]));

		const result = await getCollection("session-token", { status: "en_cours", sort: "rating", page: 1, size: 12 });

		const [url, options] = fetchMock.mock.calls[0] ?? [];
		expect(url).toBe("http://localhost:8000/me/collection?statut=en_cours&tri=note");
		expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer session-token");
		expect(result.items[0]).toMatchObject({
			id: 9,
			item_id: 4,
			status: "en_cours",
			rating: 4,
			comment: "Progression",
			item: { name: "Squat", category: "Jambes" },
		});
	});

	it("sends registration and collection bodies with the contract field names", async () => {
		fetchMock.mockResolvedValueOnce(jsonResponse({ id: 3, email: "demo@example.com" }, 201));
		await registerUser({ email: "demo@example.com", password: "password-123" });
		expect(JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body))).toEqual({
			email: "demo@example.com",
			password: "password-123",
		});

		fetchMock.mockResolvedValueOnce(jsonResponse({}));
		await addCollectionEntry("token", {
			item_id: 4,
			status: "en_cours",
			rating: 4,
			comment: "Progression",
		});
		expect(JSON.parse(String(fetchMock.mock.calls[1]?.[1]?.body))).toEqual({
			item_id: 4,
			statut: "en_cours",
			note: 4,
			commentaire: "Progression",
		});

		fetchMock.mockResolvedValueOnce(jsonResponse({}));
		await updateCollectionEntry("token", 9, { rating: 5, comment: null });
		expect(fetchMock.mock.calls[2]?.[0]).toBe("http://localhost:8000/me/collection/9");
		expect(JSON.parse(String(fetchMock.mock.calls[2]?.[1]?.body))).toEqual({
			note: 5,
			commentaire: null,
		});
	});

	it("maps catalogue responses from the French API contract", async () => {
		fetchMock.mockResolvedValue(jsonResponse({
			total: 1,
			page: 1,
			limit: 12,
			results: [{
				id: 4,
				titre: "Squat",
				categorie: "Jambes",
				description: "Exercice de jambes.",
				image_url: null,
				annee: null,
				groupe_musculaire: "Jambes",
				equipement: "Barre",
				difficulte: "Intermédiaire",
			}],
		}));

		const result = await getItems({ q: "squat", category: "Jambes", page: 1, size: 12 });

		expect(fetchMock.mock.calls[0]?.[0]).toBe(
			"http://localhost:8000/items?q=squat&categorie=Jambes&page=1&limit=12",
		);
		expect(result.items[0]).toMatchObject({ id: 4, name: "Squat", category: "Jambes" });
	});

	it("turns the API error envelope into an ApiError", async () => {
		fetchMock.mockResolvedValue(
			jsonResponse({ erreur: { code: 401, message: "Identifiants invalides" } }, 401),
		);

		try {
			await loginUser({ email: "demo@example.com", password: "incorrect" });
			expect.fail("loginUser should reject for an invalid login");
		} catch (error: unknown) {
			expect(error).toBeInstanceOf(ApiError);
			expect(error).toMatchObject({ status: 401, message: "Identifiants invalides" });
		}
	});
});