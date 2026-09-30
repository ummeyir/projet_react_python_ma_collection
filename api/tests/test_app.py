import asyncio
import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

os.environ["DATABASE_URL"] = "sqlite+aiosqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-deployment"

import jwt
import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from core.config import Settings
from main import app


def test_settings_require_explicit_database_and_strong_secret(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="sqlite+aiosqlite://", secret_key="x" * 31)


def test_backend_contract():
    with TestClient(app) as client:
        assert client.get("/").json()["message"] == "Ma Collection API"
        assert client.get("/health").json()["status"] == "ok"
        cors_preflight = client.options(
            "/items",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert cors_preflight.headers["access-control-allow-origin"] == "http://localhost:5173"

        catalog = client.get("/items", params={"page": 1, "size": 100}).json()
        assert catalog["total"] == 40
        assert len(catalog["items"]) == 40
        assert len(catalog["categories"]) >= 4
        assert client.get("/items", params={"category": "Pectoraux"}).json()["total"] == 5
        assert client.get("/items/9999").status_code == 404

        unauthorized = client.get("/me/collection")
        assert unauthorized.status_code == 401
        assert unauthorized.headers["www-authenticate"] == "Bearer"
        assert unauthorized.json()["erreur"]["code"] == 401
        suffix = uuid4().hex[:8]
        first_user = {
            "username": f"first_{suffix}",
            "email": f"first_{suffix}@example.com",
            "password": "correct-horse-123",
        }
        registration = client.post("/auth/register", json=first_user)
        assert registration.status_code == 201
        assert "hashed_password" not in registration.json()
        duplicate_registration = client.post("/auth/register", json=first_user)
        assert duplicate_registration.status_code == 409
        assert duplicate_registration.json()["erreur"]["code"] == 409

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
        duplicate_entry = client.post("/me/collection", headers=first_headers, json={"item_id": 1})
        assert duplicate_entry.status_code == 409
        assert duplicate_entry.json()["erreur"]["code"] == 409
        updated_entry = client.patch(
            "/me/collection/1",
            headers=first_headers,
            json={"status": "termine", "rating": 5, "comment": "Très bien"},
        ).json()
        assert updated_entry["status"] == "termine"
        assert updated_entry["rating"] == 5
        null_status = client.patch("/me/collection/1", headers=first_headers, json={"status": None})
        assert null_status.status_code == 422
        assert null_status.json()["erreur"]["code"] == 422
        invalid_rating = client.post(
            "/me/collection",
            headers=first_headers,
            json={"item_id": 2, "status": "en_cours", "rating": 6},
        )
        assert invalid_rating.status_code == 422
        assert invalid_rating.json()["erreur"]["code"] == 422
        filtered_collection = client.get(
            "/me/collection", headers=first_headers, params={"status": "termine", "sort": "rating"}
        ).json()
        assert filtered_collection["total"] == 1
        assert filtered_collection["items"][0]["item_id"] == 1
        first_collection_page = client.get(
            "/me/collection", headers=first_headers, params={"page": 1, "size": 1}
        ).json()
        assert first_collection_page["page"] == 1
        assert first_collection_page["size"] == 1
        assert first_collection_page["total"] == 1
        assert len(first_collection_page["items"]) == 1
        second_collection_page = client.get(
            "/me/collection", headers=first_headers, params={"page": 2, "size": 1}
        ).json()
        assert second_collection_page["total"] == 1
        assert second_collection_page["items"] == []

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
        foreign_entry = client.get("/me/collection/1", headers=second_headers)
        assert foreign_entry.status_code == 404
        assert foreign_entry.json()["erreur"] == {
            "code": 404,
            "message": "Exercice absent de votre collection",
        }
        foreign_update = client.patch(
            "/me/collection/1",
            headers=second_headers,
            json={"status": "en_cours", "rating": 1, "comment": "Modification interdite"},
        )
        assert foreign_update.status_code == 404
        assert foreign_update.json()["erreur"]["code"] == 404
        unchanged_entry = client.get("/me/collection/1", headers=first_headers).json()
        assert unchanged_entry["status"] == "termine"
        assert unchanged_entry["rating"] == 5
        assert unchanged_entry["comment"] == "Très bien"
        assert client.delete("/me/collection/1", headers=second_headers).status_code == 404

        stats = client.get("/me/stats", headers=first_headers).json()
        assert stats == {
            "total": 1,
            "by_status": {"a_decouvrir": 0, "en_cours": 0, "termine": 1},
            "average_rating": 5.0,
        }
        empty_update = client.patch("/me/collection/1", headers=first_headers, json={})
        assert empty_update.status_code == 422
        assert empty_update.json()["erreur"]["code"] == 422
        missing_item = client.post("/me/collection", headers=first_headers, json={"item_id": 9999})
        assert missing_item.status_code == 404
        assert missing_item.json()["erreur"]["code"] == 404
        invalid_token = client.get("/me/collection", headers={"Authorization": "Bearer invalid"})
        assert invalid_token.status_code == 401
        assert invalid_token.headers["www-authenticate"] == "Bearer"
        assert invalid_token.json()["erreur"]["code"] == 401

        expired_token = jwt.encode(
            {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            "test-secret-key-not-for-deployment",
            algorithm="HS256",
        )
        expired_headers = {"Authorization": f"Bearer {expired_token}"}
        expired_get = client.get("/me/collection", headers=expired_headers)
        assert expired_get.status_code == 401
        assert expired_get.json()["erreur"]["code"] == 401
        expired_patch = client.patch(
            "/me/collection/1", headers=expired_headers, json={"status": "en_cours"}
        )
        assert expired_patch.status_code == 401
        assert expired_patch.json()["erreur"]["code"] == 401
        invalid_page = client.get("/items", params={"page": 0})
        assert invalid_page.status_code == 422
        assert invalid_page.json()["erreur"]["code"] == 422
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
    from db.database import async_session_maker
    from models.entry import Entry

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

        original_commit = AsyncSession.commit

        async def insert_concurrent_duplicate(session):
            pending_entry = next(entry for entry in session.new if isinstance(entry, Entry))
            async with async_session_maker() as competing_session:
                competing_session.add(
                    Entry(user_id=pending_entry.user_id, item_id=pending_entry.item_id)
                )
                await original_commit(competing_session)
            await original_commit(session)

        monkeypatch.setattr(AsyncSession, "commit", insert_concurrent_duplicate)
        response = client.post("/me/collection", headers=headers, json={"item_id": 1})
        collection = client.get("/me/collection", headers=headers)

    assert response.status_code == 409
    assert response.json()["erreur"]["code"] == 409
    assert collection.status_code == 200
    assert collection.json()["total"] == 1


def test_seed_items_is_idempotent() -> None:
    from sqlalchemy import func, select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlmodel import SQLModel

    from models.item import Item
    from seed import seed_items

    async def verify_seed() -> None:
        seed_engine = create_async_engine("sqlite+aiosqlite://")
        async with seed_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

        session_factory = async_sessionmaker(seed_engine, class_=AsyncSession, expire_on_commit=False)
        async with session_factory() as session:
            await seed_items(session)
            await seed_items(session)
            item_count = await session.scalar(select(func.count()).select_from(Item))
            item_ids = (await session.scalars(select(Item.id).order_by(Item.id))).all()

        assert item_count == 40
        assert item_ids == list(range(1, 41))
        await seed_engine.dispose()

    asyncio.run(verify_seed())
