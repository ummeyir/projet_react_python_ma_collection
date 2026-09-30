import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { AuthProvider } from "../contexts/AuthContext";
import ProtectedRoute from "./ProtectedRoute";

const fetchMock = vi.fn<typeof fetch>();

function jsonResponse(payload: unknown, status = 200): Response {
	return new Response(JSON.stringify(payload), {
		status,
		headers: { "Content-Type": "application/json" },
	});
}

function renderProtectedRoute() {
	return render(
		<AuthProvider>
			<MemoryRouter initialEntries={["/collection"]}>
				<Routes>
					<Route element={<ProtectedRoute />}>
						<Route path="/collection" element={<p>Collection privée</p>} />
					</Route>
					<Route path="/login" element={<p>Écran de connexion</p>} />
				</Routes>
			</MemoryRouter>
		</AuthProvider>,
	);
}

beforeEach(() => {
	localStorage.clear();
	fetchMock.mockReset();
	vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
	cleanup();
	localStorage.clear();
	vi.unstubAllGlobals();
});

describe("ProtectedRoute", () => {
	it("redirects to login when there is no session", async () => {
		renderProtectedRoute();

		expect(await screen.findByText("Écran de connexion")).toBeTruthy();
		expect(fetchMock).not.toHaveBeenCalled();
	});

	it("restores a valid saved session before showing the private page", async () => {
		localStorage.setItem("ma-collection-token", JSON.stringify("saved-token"));
		fetchMock.mockResolvedValue(
			jsonResponse({ id: 2, email: "demo@example.com" }),
		);

		renderProtectedRoute();

		expect(await screen.findByText("Collection privée")).toBeTruthy();
		const [url, options] = fetchMock.mock.calls[0] ?? [];
		expect(url).toBe("http://localhost:8000/auth/me");
		expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer saved-token");
	});
});