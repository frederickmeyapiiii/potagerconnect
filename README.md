# PotagerConnect

PotagerConnect est un MVP de présentation pour un projet de jardin partagé numérique. Il illustre un produit complet en version simplifiée avec :
- la cartographie des parcelles et l’attribution aux jardiniers,
- un planning de plantation basé sur les saisons et rotations,
- une météo localisée avec conseils automatisés,
- un espace de partage de photos,
- une logique de partage des récoltes,
- un forum d’entraide et d’échange de graines/plants.

## Stack choisie
- Python + Flask
- SQLite pour la base locale
- Docker pour l’exécution rapide en local

## Lancer localement

### Sans Docker
```bash
pip install -r requirements.txt
flask --app app run
```

### Avec Docker
```bash
docker compose up --build
```

Puis ouvrir : http://localhost:5000

## Structure du projet
- app/ : application Flask
- app/templates/ : pages HTML
- app/static/ : styles CSS et JavaScript
- docs/ : documentation technique et guides
- tests/ : tests de validation du MVP

## Documentation disponible
- `docs/technical.md` : architecture, APIs, déploiement Docker
- `docs/user-guide.md` : mode d’emploi pour l’utilisateur
- `docs/admin-guide.md` : installation, configuration, maintenance
- `docs/retour-experience.md` : difficultés et solutions

## Tests
```bash
python -m unittest discover -s tests -v
```
