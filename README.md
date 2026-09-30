# Ma Collection

# Ma Collection

Application web en français pour parcourir des exercices de musculation et gérer une collection personnelle. Le backend expose une API REST en anglais ; l'interface présente les contenus et les actions en français.

## Fonctionnalités

- Catalogue d'exercices avec recherche, filtre par catégorie, pagination et fiche détaillée.
- Inscription, connexion et déconnexion avec authentification JWT.
- Collection privée paginée avec statut, note de 1 à 5 et commentaire facultatif.
- Filtre et tri des entrées, modification et suppression.
- Statistiques personnelles avec répartition par statut et note moyenne.

## Technologies

- **Backend :** Python, FastAPI, SQLModel, SQLAlchemy asynchrone et PostgreSQL.
- **Frontend :** React, TypeScript strict, Vite et React Router.
- **Infrastructure :** Docker Compose pour PostgreSQL et l'API.

## Prérequis

- Docker Desktop avec Docker Compose.
- Node.js 20.19+ ou 22.12+, et npm.

## Lancement

Depuis la racine du dépôt, crée `.env` à partir de `.env.example`, remplace les valeurs de mot de passe et génère une clé avec `python3 -c "import secrets; print(secrets.token_hex(32))"`. Puis démarre PostgreSQL et l'API :

```powershell
docker compose up --build -d
```

Dans un second terminal, démarre le frontend :

```powershell
cd web
npm ci
npm run dev
```

L'application est disponible sur <http://localhost:5173>. L'API répond sur <http://localhost:8000>, avec la documentation interactive sur <http://localhost:8000/docs>. Les 40 exercices initiaux sont insérés au démarrage de l'API.

Pour arrêter les conteneurs :

```powershell
docker compose down
```

Le volume `postgres_data` conserve la base. `docker compose down -v` supprime ce volume et toutes les données qu'il contient.

## Configuration

Compose lit `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES` et `CORS_ORIGINS` depuis `.env` à la racine. Le mot de passe PostgreSQL et la clé secrète sont obligatoires ; ne versionne jamais `.env` ni un secret de production. `CORS_ORIGINS` est une liste d'origines séparées par des virgules.

Le frontend utilise `http://localhost:8000` par défaut. Pour changer cette adresse, définis `VITE_API_BASE_URL` dans `web/.env.local`.

## Vérifications

Build frontend :

```powershell
cd web
npm run build
npm test
```

Tests backend, depuis `api/` après installation des dépendances de test :

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Sécurité

Le token JWT est stocké dans `localStorage` pour ce projet pédagogique. Le JavaScript de la page peut y accéder : une faille XSS pourrait donc voler le token. Une alternative de production est un cookie `HttpOnly`, `Secure` et `SameSite`, accompagné d'une protection CSRF adaptée.

## Structure

```text
api/    API FastAPI, modèles, schémas, routes et tests
web/    Application React/TypeScript, contextes, hooks et écrans
compose.yaml    Services PostgreSQL et API
```
