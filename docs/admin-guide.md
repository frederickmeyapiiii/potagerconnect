# Guide admin

## Installation locale
1. Cloner le dépôt.
2. Aller dans le dossier du projet.
3. Installer les dépendances :
```bash
pip install -r requirements.txt
```
4. Lancer l’application :
```bash
flask --app app run
```
5. Ouvrir `http://localhost:5000`.

## Déploiement Docker
1. Construire l’image et démarrer le service :
```bash
docker compose up --build
```
2. Accéder à l’application à `http://localhost:5000`.

## Configuration
- Le backend est dans `app/__init__.py`.
- Les templates sont dans `app/templates/`.
- Les styles et scripts sont dans `app/static/`.

## Maintenance
- Pour réinitialiser les données, supprimer le fichier de base :
```bash
rm app/data/potager.db
```
- Redémarrer ensuite l’application pour recréer la base avec les données de démonstration.
- Pour arrêter Docker :
```bash
docker compose down
```
