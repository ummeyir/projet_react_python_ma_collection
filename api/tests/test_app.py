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
        disallowed_cors = client.options(
            "/items",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" not in disallowed_cors.headers

        catalog = client.get("/items", params={"page": 1, "limit": 50}).json()
        assert catalog["total"] == 40
        assert catalog["limit"] == 50
        assert len(catalog["results"]) == 40
        assert catalog["results"][0]["titre"]
        assert catalog["results"][0]["annee"] is None
        assert "name" not in catalog["results"][0]
        assert set(catalog) == {"total", "page", "limit", "results"}
        assert client.get("/items", params={"categorie": "Pectoraux"}).json()["total"] == 5
        assert client.get("/items", params={"limit": 51}).status_code == 422
        assert client.get("/items", params={"q": ""}).status_code == 422
        assert client.get("/items/9999").status_code == 404

        unauthorized = client.get("/me/collection")
        assert unauthorized.status_code == 401
        assert unauthorized.headers["www-authenticate"] == "Bearer"
        assert unauthorized.json()["erreur"]["code"] == 401
        suffix = uuid4().hex[:8]
        first_user = {
            "email": f"first_{suffix}@example.com",
            "password": "correct-horse-123",
        }
        registration = client.post("/auth/register", json=first_user)
        assert registration.status_code == 201
        assert set(registration.json()) == {"id", "email"}
        assert "hashed_password" not in registration.json()
        duplicate_registration = client.post("/auth/register", json=first_user)
        assert duplicate_registration.status_code == 409
        assert duplicate_registration.json()["erreur"]["code"] == 409

        login = client.post(
            "/auth/login",
            json={"email": first_user["email"], "password": first_user["password"]},
        )
        assert login.status_code == 200
        assert set(login.json()) == {"access_token", "token_type"}
        first_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.get("/auth/me", headers=first_headers).json() == {
            "id": registration.json()["id"],
            "email": first_user["email"],
        }
        assert client.post("/auth/login", json={"email": first_user["email"], "password": "wrong-pass"}).status_code == 401

        add_response = client.post(
            "/me/collection",
            headers=first_headers,
            json={"item_id": 1, "statut": "en_cours", "note": 4, "commentaire": "Progression"},
        )
        assert add_response.status_code == 201
        assert set(add_response.json()) == {
            "id", "statut", "note", "commentaire", "date_ajout", "item"
        }
        assert add_response.json()["item"]["titre"] == "Développé couché"
        assert set(add_response.json()["item"]) == {
            "id", "titre", "categorie", "description", "image_url", "annee",
            "groupe_musculaire", "equipement", "difficulte",
        }
        assert add_response.json()["statut"] == "en_cours"
        assert add_response.json()["note"] == 4
        assert "item_id" not in add_response.json()
        entry_id = add_response.json()["id"]
        duplicate_entry = client.post("/me/collection", headers=first_headers, json={"item_id": 1})
        assert duplicate_entry.status_code == 409
        assert duplicate_entry.json()["erreur"]["code"] == 409
        updated_entry = client.patch(
            f"/me/collection/{entry_id}",
            headers=first_headers,
            json={"statut": "termine", "note": 5, "commentaire": "Très bien"},
        ).json()
        assert updated_entry["statut"] == "termine"
        assert updated_entry["note"] == 5
        null_status = client.patch(
            f"/me/collection/{entry_id}", headers=first_headers, json={"statut": None}
        )
        assert null_status.status_code == 400
        assert null_status.json()["erreur"]["code"] == 400
        invalid_rating = client.post(
            "/me/collection",
            headers=first_headers,
            json={"item_id": 2, "statut": "en_cours", "note": 6},
        )
        assert invalid_rating.status_code == 422
        assert invalid_rating.json()["erreur"]["code"] == 422
        filtered_collection = client.get(
            "/me/collection", headers=first_headers, params={"statut": "termine", "tri": "note"}
        ).json()
        assert len(filtered_collection) == 1
        assert isinstance(filtered_collection, list)
        assert filtered_collection[0]["id"] == entry_id
        assert filtered_collection[0]["statut"] == "termine"

        second_user = {
            "email": f"second_{suffix}@example.com",
            "password": "correct-horse-456",
        }
        client.post("/auth/register", json=second_user).raise_for_status()
        second_login = client.post(
            "/auth/login", json={"email": second_user["email"], "password": second_user["password"]}
        )
        second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
        foreign_entry = client.get(f"/me/collection/{entry_id}", headers=second_headers)
        assert foreign_entry.status_code == 404
        assert foreign_entry.json()["erreur"] == {
            "code": 404,
            "message": "Exercice absent de votre collection",
        }
        foreign_update = client.patch(
            f"/me/collection/{entry_id}",
            headers=second_headers,
            json={"statut": "en_cours", "note": 1, "commentaire": "Modification interdite"},
        )
        assert foreign_update.status_code == 404
        assert foreign_update.json()["erreur"]["code"] == 404
        unchanged_entry = client.get(f"/me/collection/{entry_id}", headers=first_headers).json()
        assert unchanged_entry["statut"] == "termine"
        assert unchanged_entry["note"] == 5
        assert unchanged_entry["commentaire"] == "Très bien"
        assert client.delete(f"/me/collection/{entry_id}", headers=second_headers).status_code == 404

        stats = client.get("/me/stats", headers=first_headers).json()
        assert set(stats) == {"total", "par_statut", "note_moyenne"}
        assert stats == {
            "total": 1,
            "par_statut": {"a_decouvrir": 0, "en_cours": 0, "termine": 1},
            "note_moyenne": 5.0,
        }
        empty_update = client.patch(f"/me/collection/{entry_id}", headers=first_headers, json={})
        assert empty_update.status_code == 400
        assert empty_update.json()["erreur"]["code"] == 400
        openapi = client.get("/openapi.json").json()
        patch_docs = openapi["paths"]["/me/collection/{entry_id}"]["patch"]
        assert "400" in patch_docs["responses"]
        assert patch_docs["summary"] == "Modifier une entrée de collection"
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
            f"/me/collection/{entry_id}", headers=expired_headers, json={"statut": "en_cours"}
        )
        assert expired_patch.status_code == 401
        assert expired_patch.json()["erreur"]["code"] == 401
        invalid_page = client.get("/items", params={"page": 0})
        assert invalid_page.status_code == 422
        assert invalid_page.json()["erreur"]["code"] == 422
        assert client.delete(f"/me/collection/{entry_id}", headers=first_headers).status_code == 204
        assert client.get("/me/collection", headers=first_headers).json() == []

        invalid = client.post("/auth/register", json={"email": "invalid", "password": "123"})
        assert invalid.status_code == 422
        assert invalid.json()["erreur"]["code"] == 422


def test_existing_entry_schema_migrates_safely() -> None:
    from sqlalchemy import inspect, text
    from sqlalchemy.ext.asyncio import create_async_engine

    from db.database import _migrate_entry_columns, _migrate_item_columns

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
            await connection.execute(text("CREATE TABLE item (id INTEGER PRIMARY KEY)"))
            await connection.execute(
                text(
                    "INSERT INTO entry (id, user_id, item_id, is_favorite, notes, added_at) "
                    "VALUES (1, 2, 3, 1, 'Ancien commentaire', '2026-01-01T00:00:00Z')"
                )
            )
            await connection.run_sync(_migrate_entry_columns)
            await connection.run_sync(_migrate_item_columns)
            item_columns = await connection.run_sync(
                lambda sync_connection: {column["name"] for column in inspect(sync_connection).get_columns("item")}
            )
            assert "year" in item_columns
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
    assert len(collection.json()) == 1


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


def test_seed_main_initializes_and_closes_database(monkeypatch) -> None:
    import seed
    from db import database

    events = []
    session = object()

    class SessionContext:
        async def __aenter__(self):
            events.append("session_open")
            return session

        async def __aexit__(self, exc_type, exc_value, traceback):
            events.append("session_close")

    class FakeEngine:
        async def dispose(self):
            events.append("engine_dispose")

    async def create_tables():
        events.append("create_tables")

    async def run_seed(session_arg):
        assert session_arg is session
        events.append("seed")

    monkeypatch.setattr(database, "async_session_maker", SessionContext)
    monkeypatch.setattr(database, "create_db_and_tables", create_tables)
    monkeypatch.setattr(database, "engine", FakeEngine())
    monkeypatch.setattr(seed, "seed_items", run_seed)

    asyncio.run(seed.main())

    assert events == ["create_tables", "session_open", "seed", "session_close", "engine_dispose"]
