import asyncio
import os
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-deployment"

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
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

        add_response = client.post(
            "/me/collection",
            headers=first_headers,
            json={"item_id": 1, "status": "en_cours", "rating": 4, "comment": "Progression"},
        )
        assert add_response.status_code == 201
        assert add_response.json()["item"]["name"] == "Développé couché"
        assert add_response.json()["status"] == "en_cours"
        assert add_response.json()["rating"] == 4
        assert client.post("/me/collection", headers=first_headers, json={"item_id": 1}).status_code == 409
        updated_entry = client.patch(
            "/me/collection/1",
            headers=first_headers,
            json={"status": "termine", "rating": 5, "comment": "Très bien"},
        ).json()
        assert updated_entry["status"] == "termine"
        assert updated_entry["rating"] == 5
        assert client.patch("/me/collection/1", headers=first_headers, json={"status": None}).status_code == 422
        assert client.post(
            "/me/collection",
            headers=first_headers,
            json={"item_id": 2, "status": "en_cours", "rating": 6},
        ).status_code == 422
        filtered_collection = client.get(
            "/me/collection", headers=first_headers, params={"status": "termine", "sort": "rating"}
        ).json()
        assert filtered_collection["total"] == 1
        assert filtered_collection["items"][0]["item_id"] == 1

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
        assert client.patch(
            "/me/collection/1", headers=second_headers, json={"status": "termine"}
        ).status_code == 404
        assert client.delete("/me/collection/1", headers=second_headers).status_code == 404

        stats = client.get("/me/stats", headers=first_headers).json()
        assert stats == {
            "total": 1,
            "by_status": {"a_decouvrir": 0, "en_cours": 0, "termine": 1},
            "average_rating": 5.0,
        }
        empty_update = client.patch("/me/collection/1", headers=first_headers, json={})
        assert empty_update.status_code == 422
        assert client.post("/me/collection", headers=first_headers, json={"item_id": 9999}).status_code == 404
        assert client.get("/me/collection", headers={"Authorization": "Bearer invalid"}).status_code == 401
        assert client.get("/items", params={"page": 0}).status_code == 422
        assert client.delete("/me/collection/1", headers=first_headers).status_code == 204
        assert client.get("/me/collection", headers=first_headers).json()["total"] == 0

        invalid = client.post("/auth/register", json={"username": "x", "email": "invalid", "password": "123"})
        assert invalid.status_code == 422
        assert invalid.json()["erreur"]["code"] == 422


def test_existing_entry_schema_migrates_safely() -> None:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    from db.database import _migrate_entry_columns

    async def verify_migration() -> None:
        migration_engine = create_async_engine("sqlite+aiosqlite://")
        async with migration_engine.begin() as connection:
            await connection.execute(
                text(
                    "CREATE TABLE entry ("
                    "id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, item_id INTEGER NOT NULL, "
                    "is_favorite BOOLEAN NOT NULL, notes TEXT, added_at DATETIME NOT NULL)"
                )
            )
            await connection.execute(
                text(
                    "INSERT INTO entry (id, user_id, item_id, is_favorite, notes, added_at) "
                    "VALUES (1, 2, 3, 1, 'Ancien commentaire', '2026-01-01T00:00:00Z')"
                )
            )
            await connection.run_sync(_migrate_entry_columns)
            result = await connection.execute(
                text("SELECT is_favorite, notes, status, rating, comment FROM entry WHERE id = 1")
            )
            assert result.one() == (1, "Ancien commentaire", "a_decouvrir", None, "Ancien commentaire")
        await migration_engine.dispose()

    asyncio.run(verify_migration())


def test_duplicate_collection_race_returns_conflict(monkeypatch):
    suffix = uuid4().hex[:8]
    user = {
        "username": f"race_{suffix}",
        "email": f"race_{suffix}@example.com",
        "password": "correct-horse-789",
    }

    with TestClient(app) as client:
        assert client.post("/auth/register", json=user).status_code == 201
        login = client.post(
            "/auth/login", json={"email": user["email"], "password": user["password"]}
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        async def reject_duplicate_commit(_session):
            raise IntegrityError("INSERT", {}, RuntimeError("unique constraint"))

        monkeypatch.setattr(AsyncSession, "commit", reject_duplicate_commit)
        response = client.post("/me/collection", headers=headers, json={"item_id": 1})

    assert response.status_code == 409
    assert response.json()["erreur"]["code"] == 409
