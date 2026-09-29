import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, getCollection, loginUser } from "./apiClient";

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
		fetchMock.mockResolvedValue(jsonResponse({ items: [], total: 0 }));

		await getCollection("session-token", { status: "en_cours", sort: "rating" });

		const [url, options] = fetchMock.mock.calls[0] ?? [];
		expect(url).toBe("http://localhost:8000/me/collection?status=en_cours&sort=rating");
		expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer session-token");
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