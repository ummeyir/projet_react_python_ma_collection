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

- Docker Engine avec Docker Compose, ou Docker Desktop.
- Node.js 22.13+ et npm.

## Lancement

Depuis la racine du dépôt, crée le fichier local `.env` à partir du modèle :

```bash
cp .env.example .env
```

Sous PowerShell, utilise plutôt :

```powershell
Copy-Item .env.example .env
```

Génère deux valeurs aléatoires distinctes avec cette commande (exécute-la deux fois) :

```bash
node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"
```

Colle la première valeur dans `POSTGRES_PASSWORD` et la seconde dans `SECRET_KEY` dans `.env`. La clé JWT doit faire au moins 32 caractères. Garde ce fichier local : il est ignoré par Git et ne doit pas être partagé.

Démarre ensuite PostgreSQL et l'API depuis la racine :

```bash
docker compose up --build -d
```

Sur Linux, si Docker répond `permission denied` pour son socket, relance avec `sudo` :

```bash
sudo docker compose up --build -d
```

Dans un second terminal, démarre le frontend :

```bash
cd web
npm ci
npm run dev
```

L'application est disponible sur <http://localhost:5173>. L'API répond sur <http://localhost:8000>, avec la documentation interactive sur <http://localhost:8000/docs>. Les 40 exercices initiaux sont insérés au démarrage de l'API.

Pour arrêter les conteneurs :

```bash
docker compose down
```

Le volume `postgres_data` conserve la base. `docker compose down -v` supprime ce volume et toutes les données qu'il contient.

## Configuration

Compose lit `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `SECRET_KEY` et `ACCESS_TOKEN_EXPIRE_MINUTES` depuis `.env` à la racine. Le mot de passe PostgreSQL et la clé secrète sont obligatoires ; la clé doit faire au moins 32 caractères. Ne versionne jamais `.env` ni un secret de production.

Le backend autorise actuellement l'origine frontend `http://localhost:5173` dans `api/main.py`. Si le frontend utilise une autre origine, adapte cette configuration CORS. Le frontend utilise `http://localhost:8000` par défaut pour l'API. Pour configurer cette valeur explicitement, copie `web/.env.example` vers `web/.env.local`.

## Vérifications

Build frontend :

```bash
cd web
npm run build
npm test
```

Tests backend, depuis `api/` après installation des dépendances de test :

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Le seed est exécuté automatiquement au démarrage de l'API. Pour le relancer manuellement dans le conteneur :

```bash
docker compose exec api python seed.py
```

## Sécurité

Le token JWT est stocké dans `localStorage` pour ce projet pédagogique. Le JavaScript de la page peut y accéder : une faille XSS pourrait donc voler le token. Une alternative de production est un cookie `HttpOnly`, `Secure` et `SameSite`, accompagné d'une protection CSRF adaptée.

## Structure

```text
api/    API FastAPI, modèles, schémas, routes et tests
web/    Application React/TypeScript, contextes, hooks et écrans
compose.yaml    Services PostgreSQL et API
```
