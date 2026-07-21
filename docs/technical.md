# Documentation technique

## Architecture
- Backend : Flask
- Frontend : HTML/CSS/JavaScript
- Base de données : SQLite

## Composants principaux
- `app/__init__.py` : application Flask, routes, logique métier, initialisation de la base.
- `app/templates/` : gabarits Jinja pour les pages.
- `app/static/style.css` : styles du site.
- `app/static/app.js` : interaction JavaScript pour le forum, le carrousel et le modal.
- `Dockerfile` : image Docker de l’application.
- `docker-compose.yml` : configuration Docker Compose.

## APIs REST
- `GET /api/plots` : liste des parcelles.
- `GET /api/tasks` : liste des tâches.
- `GET /api/posts` : liste des messages du forum.
- `POST /api/posts` : création d’un message dans le forum.
- `POST /api/plots` : création d’une nouvelle parcelle.
- `PUT /api/plots/<id>` : mise à jour d’une parcelle.
- `DELETE /api/plots/<id>` : suppression d’une parcelle.

## Déploiement
1. Construire l’image Docker :
```bash
docker compose build
```
2. Lancer l’application :
```bash
docker compose up -d
```
3. Ouvrir : `http://localhost:5000`

## Schéma de base de données
Tables principales :
- `plots`
- `tasks`
- `weather_advice`
- `photos`
- `harvests`
- `posts`

Chaque table se crée automatiquement au démarrage si elle n’existe pas.
