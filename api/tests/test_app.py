import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-deployment"

from fastapi.testclient import TestClient

from main import app


def test_backend_contract():
    with TestClient(app) as client:
        assert client.get("/").json()["message"] == "Ma Collection API"
        assert client.get("/health").json()["status"] == "ok"

        catalog = client.get("/items", params={"page": 1, "size": 100}).json()
        assert catalog["total"] == 40
        assert len(catalog["items"]) == 40
        assert len(catalog["categories"]) >= 4
        assert client.get("/items", params={"category": "Pectoraux"}).json()["total"] == 5
        assert client.get("/items/9999").status_code == 404

        unauthorized = client.get("/me/collection")
        assert unauthorized.status_code == 401
        assert unauthorized.headers["www-authenticate"] == "Bearer"
        suffix = uuid4().hex[:8]
        first_user = {
            "username": f"first_{suffix}",
            "email": f"first_{suffix}@example.com",
            "password": "correct-horse-123",
        }
        registration = client.post("/auth/register", json=first_user)
        assert registration.status_code == 201
        assert "hashed_password" not in registration.json()
        assert client.post("/auth/register", json=first_user).status_code == 409

        login = client.post(
            "/auth/login",
            json={"email": first_user["email"], "password": first_user["password"]},
        )
        assert login.status_code == 200
        first_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.get("/auth/me", headers=first_headers).json()["username"] == first_user["username"]
        assert client.post("/auth/login", json={"email": first_user["email"], "password": "wrong-pass"}).status_code == 401

        add_response = client.post("/me/collection", headers=first_headers, json={"item_id": 1})
        assert add_response.status_code == 201
        assert add_response.json()["item"]["name"] == "Développé couché"
        assert client.post("/me/collection", headers=first_headers, json={"item_id": 1}).status_code == 409
        assert client.patch(
            "/me/collection/1", headers=first_headers, json={"is_favorite": True, "notes": "Progression"}
        ).json()["is_favorite"] is True
        assert client.patch(
            "/me/collection/1", headers=first_headers, json={"is_favorite": None}
        ).status_code == 422

        second_user = {
            "username": f"second_{suffix}",
            "email": f"second_{suffix}@example.com",
            "password": "correct-horse-456",
        }
        client.post("/auth/register", json=second_user).raise_for_status()
        second_login = client.post(
            "/auth/login", json={"email": second_user["email"], "password": second_user["password"]}
        )
        second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
        assert client.get("/me/collection/1", headers=second_headers).status_code == 404
        assert client.delete("/me/collection/1", headers=second_headers).status_code == 404

        stats = client.get("/me/stats", headers=first_headers).json()
        assert stats == {"total_items": 40, "total_collection": 1, "favorite_count": 1}
        assert client.delete("/me/collection/1", headers=first_headers).status_code == 204
        assert client.get("/me/collection", headers=first_headers).json()["total"] == 0

        invalid = client.post("/auth/register", json={"username": "x", "email": "invalid", "password": "123"})
        assert invalid.status_code == 422
        assert invalid.json()["erreur"]["code"] == 422
