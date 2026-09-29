# API backend

API FastAPI asynchrone pour le catalogue d'exercices et les collections personnelles. PostgreSQL est la base par défaut; SQLite asynchrone reste disponible pour les tests et le développement local.

## Lancement avec Docker

Depuis la racine du dépôt:

```bash
docker compose up --build
```

PostgreSQL est disponible dans le réseau Compose sous le nom `db`; l'API est publiée sur `http://localhost:8000`. La documentation interactive est sur `/docs`. Les données sont conservées dans le volume `postgres_data`; `docker compose down` ne le supprime pas. N'utilisez `docker compose down -v` que pour effacer la base.

Les valeurs de développement sont définies dans `compose.yaml`. Avant un déploiement, définissez au minimum `SECRET_KEY`, `POSTGRES_PASSWORD` et `POSTGRES_USER` dans l'environnement Compose, avec des valeurs fortes. Le secret JWT doit rester stable entre redémarrages.

## Lancement local

Python 3.11 ou supérieur et un PostgreSQL accessible sont requis pour lancer l'API avec sa configuration par défaut.

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL='postgresql+asyncpg://collection:collection@localhost:5432/collection'
export SECRET_KEY='replace-with-a-long-random-secret'
uvicorn main:app --reload
```

Pour un démarrage local sans PostgreSQL, configurez `DATABASE_URL=sqlite+aiosqlite:///./ma_collection.db`. SQLite n'est pas le défaut Compose.

## Contrat API

- `GET /items?q=&category=&difficulty=&page=1&size=12`: catalogue paginé, filtres et catégories disponibles.
- `GET /items/{item_id}`: détail d'un exercice.
- `POST /auth/register`: inscription (`username`, `email`, `password`); retourne le profil sans hash.
- `POST /auth/login`: connexion par email; retourne `access_token`, `token_type` et `user`.
- `GET /auth/me`: profil de l'utilisateur authentifié.
- `GET /me/collection?status=&sort=date|rating`: collection filtrée et triée de l'utilisateur authentifié.
- `POST /me/collection` avec `item_id`, `status`, `rating` et `comment`: ajout d'un exercice à la collection.
- `GET /me/collection/{item_id}`, `PATCH /me/collection/{item_id}` et `DELETE /me/collection/{item_id}`: consultation, modification et suppression d'une entrée appartenant à l'utilisateur.
- `GET /me/stats`: total de la collection, répartition `by_status` et `average_rating`.
- `GET /health`: vérifie la connexion à la base.

Les routes privées attendent `Authorization: Bearer <access_token>`. Les doublons retournent `409`, les ressources absentes `404`, les entrées invalides `422` et une authentification absente ou invalide `401`. Les erreurs utilisent l'enveloppe `{ "erreur": { "code": ..., "message": ... } }`.

## Tests

```bash
cd api
pip install -r requirements-dev.txt
python -m pytest -q
```

Les tests configurent une base SQLite en mémoire et n'exigent pas de service PostgreSQL.
