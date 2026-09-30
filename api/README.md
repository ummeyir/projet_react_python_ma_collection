# Backend API

FastAPI backend for **Ma Collection**. It exposes the exercise catalogue, authentication, personal collections and statistics. PostgreSQL is provided through Docker Compose.

## Run with Docker Compose

From the repository root, create `.env` from the root `.env.example`, set `POSTGRES_PASSWORD`, and set a random `SECRET_KEY` of at least 32 characters. Then start the database and API:

```sh
docker compose up --build -d
```

The API is available at <http://localhost:8000> and its interactive documentation at <http://localhost:8000/docs>. On startup, the API creates or migrates the schema and seeds the 40 catalogue items. To run the idempotent seed manually while the services are running:

```sh
docker compose exec api python seed.py
```

## Local commands

From this directory, install the development dependencies and run the tests:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

`python seed.py` runs the standalone seed command. It requires `DATABASE_URL` and `SECRET_KEY` to be available in the environment or in an `api/.env` file.

## Layout

- `routers/`: HTTP endpoints
- `schemas/`: request and response models
- `models/`: SQLModel database tables
- `dependencies/`: database, authentication and pagination dependencies
- `core/`: settings, password hashing and JWT helpers
- `db/`: async database engine, schema setup and migrations
