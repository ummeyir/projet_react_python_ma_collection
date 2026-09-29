# Ma Collection

Application web de gestion d'une collection personnelle. Le projet est organisé en deux parties : une API en Python avec FastAPI et une interface prévue en React, TypeScript et Vite.

> **État du projet :** le dépôt contient actuellement un prototype backend autour d'un catalogue d'exercices de fitness. Il ne respecte pas encore l'intégralité du contrat « Ma Collection » fourni pour le projet. Le frontend et plusieurs fichiers de configuration web sont vides ; le démarrage complet de l'application n'est donc pas encore possible.

## Fonctionnalités prévues

- Parcourir un catalogue, rechercher des éléments et consulter leur fiche détaillée.
- Créer un compte et se connecter.
- Ajouter des éléments à sa collection, suivre leur statut, leur attribuer une note et un commentaire.
- Consulter des statistiques sur sa collection.

Ces fonctionnalités décrivent l'objectif du projet. Voir la section [État actuel et limites](#état-actuel-et-limites) pour les éléments déjà présents dans le code.

## Technologies

- **API :** Python, FastAPI, SQLModel / SQLAlchemy async, SQLite, aiosqlite et JWT.
- **Interface prévue :** React, TypeScript et Vite.

## Prérequis

- Python 3.10 ou ultérieur.
- Node.js et npm seront nécessaires lorsque le frontend sera configuré.

## Démarrer l'API

Les commandes suivantes sont prévues pour PowerShell, depuis la racine du dépôt :

```powershell
cd api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(32))")
python -m uvicorn main:app --reload
```

La variable `SECRET_KEY` est nécessaire au chargement de la configuration. La commande ci-dessus génère une clé temporaire pour la session PowerShell en cours ; conservez ce terminal ouvert pendant l'utilisation de l'API. La configuration est prévue pour lire `api/.env`, mais la dépendance nécessaire à cette lecture n'est pas encore déclarée dans `api/requirements.txt`.

Une fois le serveur démarré :

- API : <http://localhost:8000>
- Documentation interactive FastAPI : <http://localhost:8000/docs>
- Vérification de santé : <http://localhost:8000/health>

Pour arrêter le serveur, utilisez `Ctrl+C` dans son terminal.

## Démarrer l'interface

Le socle React, TypeScript et Vite est en place. Depuis la racine du dépôt, démarrez l'interface avec :

```powershell
cd web
npm install
npm run dev
```

Vite sert l'interface sur <http://localhost:5173>. Pour vérifier le typage strict et créer le build de production, exécutez `npm run build` depuis `web/`. L'écran actuel est un point de départ : le catalogue, l'authentification et le branchement à l'API restent à développer.

## Vérifications

Les tests backend existants vérifient les routes `/` et `/health`. Les dépendances de test ne figurent pas dans `api/requirements.txt` ; installez-les dans l'environnement virtuel avant de les exécuter :

```powershell
python -m pip install pytest httpx
python -m pytest
```

Lancez ces commandes depuis `api/`, dans le même terminal où `SECRET_KEY` est définie.

## Structure du dépôt

```text
api/
  core/           Configuration et gestion des erreurs
  db/             Connexion à la base de données
  dependencies/   Dépendances FastAPI
  models/         Modèles de données
  routers/        Routes de l'API
  schemas/        Schémas de données
  tests/          Tests backend
  main.py         Assemblage de l'application
  seed.py         Données d'exercices en mémoire
web/
  src/            Écrans, composants, hooks et services prévus
```

## État actuel et limites

- `GET /` et `GET /health` sont disponibles.
- `GET /items` et `GET /items/{item_id}` exposent un catalogue statique de 40 exercices défini dans `api/seed.py`. Le catalogue n'est pas peuplé dans SQLite par un script exécutable.
- `POST /auth/register` et `POST /auth/login` renvoient des réponses de démonstration ; l'authentification réelle et les jetons JWT ne sont pas encore implémentés.
- Les routes de collection et de statistiques renvoient des données de démonstration. Leurs chemins et formats ne correspondent pas encore au contrat imposé (`/me/collection` et `/me/stats`).
- Le socle React/TypeScript/Vite est initialisé et compilable, mais l'interface métier, les contextes, les hooks et le client HTTP restent à développer.
- Le fichier `api/.env.example` est vide. Aucun secret ne doit être ajouté au dépôt ; configurez `SECRET_KEY` localement.

Le README décrit ainsi le lancement du prototype disponible et signale les étapes restant nécessaires avant une démonstration complète conforme au cahier des charges.
