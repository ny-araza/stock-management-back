# Stock Management Back - Docker (développement)

## Lancer les services

```bash
docker compose up --build
```

## Exécuter les migrations Django

Dans un autre terminal, depuis la racine du dépôt :

```bash
docker compose exec backend python manage.py migrate
```

## Vérifier l'API

Ouvrez :

- http://localhost:8000/api/

## Configuration frontend Docker (React/Vite)

Le frontend exécuté dans le navigateur doit appeler l'API via :

- `http://localhost:8000/api`

Important : ici `localhost` correspond à la machine du navigateur (votre PC), pas au réseau interne Docker.
Ne remplacez donc pas cette URL par `http://backend:8000/api` côté frontend navigateur.

## Variables d'environnement utiles

Les valeurs locales restent celles utilisées historiquement par défaut :

- `DB_NAME` (défaut: `db_baby`)
- `DB_HOST` (défaut Django local: `localhost`, et `db` dans `docker-compose.yml`)
- `DB_USER` (défaut: `root`)
- `DB_PASSWORD` (défaut: `root`)
- `DB_PORT` (défaut: `3306`)
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`

Si le frontend est servi via une autre origine (ex: autre port/nom d'hôte), ajoutez cette origine dans `CORS_ALLOWED_ORIGINS` et `CSRF_TRUSTED_ORIGINS`.
