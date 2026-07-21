import os
import sqlite3
import requests
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "potager.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS plots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            gardener TEXT NOT NULL,
            status TEXT NOT NULL,
            season TEXT NOT NULL,
            crop TEXT NOT NULL,
            rotation TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            priority TEXT NOT NULL,
            season TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS weather_advice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            temperature TEXT NOT NULL,
            condition TEXT NOT NULL,
            advice TEXT NOT NULL,
            humidity TEXT,
            wind TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            caption TEXT NOT NULL,
            image_url TEXT NOT NULL,
            plot_id INTEGER,
            date_taken TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (plot_id) REFERENCES plots (id)
        );

        CREATE TABLE IF NOT EXISTS harvests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            quantity TEXT NOT NULL,
            gardener TEXT NOT NULL,
            location TEXT NOT NULL,
            harvest_date TEXT DEFAULT CURRENT_TIMESTAMP,
            distributed BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            message TEXT NOT NULL,
            kind TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    columns = conn.execute("PRAGMA table_info(posts)").fetchall()
    if columns and not any(col[1] == 'kind' for col in columns):
        conn.execute("ALTER TABLE posts ADD COLUMN kind TEXT NOT NULL DEFAULT 'Forum'")
        conn.commit()

    conn.commit()
    conn.close()


def seed_data():
    conn = get_db_connection()

    if conn.execute("SELECT COUNT(*) as count FROM plots").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO plots (name, gardener, status, season, crop, rotation) VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("Parcelle Sud", "Mina", "En croissance", "Été", "Tomates", "Rotation 1"),
                ("Parcelle Est", "Julien", "À planter", "Printemps", "Carottes", "Rotation 2"),
                ("Mini potager", "Aïcha", "Prêt à récolter", "Automne", "Courges", "Rotation 3"),
                ("Jardin collectif", "Samir", "À surveiller", "Été", "Basilic", "Rotation 1"),
            ],
        )

    if conn.execute("SELECT COUNT(*) as count FROM tasks").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO tasks (title, detail, priority, season) VALUES (?, ?, ?, ?)",
            [
                ("Arroser les salades", "3 fois cette semaine pour éviter le stress thermique", "Haute", "Été"),
                ("Répartir les semences", "Préparer la rotation du mois prochain", "Moyenne", "Printemps"),
                ("Nettoyer le coin compost", "Avant la récolte du week-end", "Faible", "Automne"),
                ("Installer les supports", "Pour les haricots grimpants", "Haute", "Printemps"),
            ],
        )

    if conn.execute("SELECT COUNT(*) as count FROM weather_advice").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO weather_advice (city, temperature, condition, advice) VALUES (?, ?, ?, ?)",
            [
                ("Lyon", "24°C", "Soleil", "Protéger les jeunes plants en fin de journée."),
                ("Paris", "19°C", "Nuageux", "Idéal pour semer des graines de courgettes."),
            ],
        )

    if conn.execute("SELECT COUNT(*) as count FROM photos").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO photos (title, caption, image_url) VALUES (?, ?, ?)",
            [
                ("Tomates en croissance", "Évolution rapide après la pluie", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=800&q=80"),
                ("Potager urbain", "Une parcelle bien organisée pour la communauté", "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?auto=format&fit=crop&w=800&q=80"),
                ("Récolte de courges", "Le partage a déjà commencé", "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80"),
            ],
        )

    if conn.execute("SELECT COUNT(*) as count FROM harvests").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO harvests (crop, quantity, gardener, location) VALUES (?, ?, ?, ?)",
            [
                ("Salades", "12 bottes", "Mina", "Parcelle Sud"),
                ("Radis", "20 poignées", "Julien", "Parcelle Est"),
                ("Courgettes", "8 pièces", "Aïcha", "Mini potager"),
            ],
        )

    if conn.execute("SELECT COUNT(*) as count FROM posts").fetchone()["count"] == 0:
        conn.executemany(
            "INSERT INTO posts (author, message, kind) VALUES (?, ?, ?)",
            [
                ("Sofia", "Les conseils météo ont vraiment aidé à protéger les tomates ce matin.", "Conseil"),
                ("Nadia", "Je peux partager 6 plants de basilic à la fin de la semaine.", "Échange"),
                ("Omar", "Qui veut échanger des graines de courgettes ?", "Forum"),
            ],
        )

    conn.commit()
    conn.close()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["JSON_SORT_KEYS"] = False

    init_db()
    seed_data()

    @app.route("/")
    def index():
        conn = get_db_connection()
        plots = conn.execute("SELECT * FROM plots ORDER BY id").fetchall()
        tasks = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        weather = conn.execute("SELECT * FROM weather_advice ORDER BY id").fetchall()
        photos = conn.execute("SELECT * FROM photos ORDER BY id").fetchall()
        harvests = conn.execute("SELECT * FROM harvests ORDER BY id").fetchall()
        posts = conn.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 8").fetchall()
        
        # Calculer les statistiques pour l'impact social
        total_plots = len(plots)
        active_plots = len([p for p in plots if p['status'] in ['En croissance', 'Prêt à récolter']])
        total_harvests = len(harvests)
        distributed_harvests = len([h for h in harvests if h['distributed'] == 1])
        total_posts = len(posts)
        total_gardeners = len(set(p['gardener'] for p in plots))
        
        stats = {
            'total_plots': total_plots,
            'active_plots': active_plots,
            'total_harvests': total_harvests,
            'distributed_harvests': distributed_harvests,
            'total_posts': total_posts,
            'total_gardeners': total_gardeners
        }
        
        conn.close()
        return render_template(
            "index.html",
            plots=plots,
            tasks=tasks,
            weather=weather,
            photos=photos,
            harvests=harvests,
            posts=posts,
            stats=stats,
        )

    @app.route("/api/plots")
    def api_plots():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM plots ORDER BY id").fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.route("/api/plots", methods=["POST"])
    def create_plot():
        payload = request.get_json(silent=True) or {}
        name = payload.get("name", "").strip()
        gardener = payload.get("gardener", "").strip()
        status = payload.get("status", "À planter").strip()
        season = payload.get("season", "Printemps").strip()
        crop = payload.get("crop", "").strip()
        rotation = payload.get("rotation", "Rotation 1").strip()

        if not name or not gardener or not crop:
            return jsonify({"error": "Champs manquants"}), 400

        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO plots (name, gardener, status, season, crop, rotation) VALUES (?, ?, ?, ?, ?, ?)",
            (name, gardener, status, season, crop, rotation),
        )
        conn.commit()
        conn.close()
        return jsonify({"id": cursor.lastrowid, "name": name, "gardener": gardener, "status": status, "season": season, "crop": crop, "rotation": rotation}), 201

    @app.route("/api/plots/<int:plot_id>", methods=["PUT"])
    def update_plot(plot_id):
        payload = request.get_json(silent=True) or {}
        conn = get_db_connection()
        plot = conn.execute("SELECT * FROM plots WHERE id = ?", (plot_id,)).fetchone()
        if not plot:
            conn.close()
            return jsonify({"error": "Parcelle non trouvée"}), 404
        
        name = payload.get("name", plot["name"]).strip()
        gardener = payload.get("gardener", plot["gardener"]).strip()
        status = payload.get("status", plot["status"]).strip()
        season = payload.get("season", plot["season"]).strip()
        crop = payload.get("crop", plot["crop"]).strip()
        rotation = payload.get("rotation", plot["rotation"]).strip()
        
        conn.execute(
            "UPDATE plots SET name = ?, gardener = ?, status = ?, season = ?, crop = ?, rotation = ? WHERE id = ?",
            (name, gardener, status, season, crop, rotation, plot_id),
        )
        conn.commit()
        conn.close()
        return jsonify({"id": plot_id, "name": name, "gardener": gardener, "status": status, "season": season, "crop": crop, "rotation": rotation}), 200

    @app.route("/api/plots/<int:plot_id>", methods=["DELETE"])
    def delete_plot(plot_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM plots WHERE id = ?", (plot_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Parcelle supprimée"}), 200

    @app.route("/api/tasks")
    def api_tasks():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "").strip()
        detail = payload.get("detail", "").strip()
        priority = payload.get("priority", "Moyenne").strip()
        season = payload.get("season", "Printemps").strip()

        if not title or not detail:
            return jsonify({"error": "Champs manquants"}), 400

        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO tasks (title, detail, priority, season) VALUES (?, ?, ?, ?)",
            (title, detail, priority, season),
        )
        conn.commit()
        conn.close()
        return jsonify({"id": cursor.lastrowid, "title": title, "detail": detail, "priority": priority, "season": season}), 201

    @app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
    def delete_task(task_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Tâche supprimée"}), 200

    @app.route("/api/posts")
    def api_posts():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.route("/api/posts", methods=["POST"])
    def create_post():
        payload = request.get_json(silent=True) or {}
        author = (payload.get("author") or "Anonyme").strip()
        message = (payload.get("message") or "").strip()
        kind = (payload.get("kind") or "Forum").strip()

        if not message:
            return jsonify({"error": "Le message est vide"}), 400

        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO posts (author, message, kind) VALUES (?, ?, ?)",
            (author, message, kind),
        )
        conn.commit()
        conn.close()
        return jsonify({"id": cursor.lastrowid, "author": author, "message": message, "kind": kind}), 201

    @app.route("/api/harvests")
    def api_harvests():
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM harvests ORDER BY id").fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.route("/api/harvests", methods=["POST"])
    def create_harvest():
        payload = request.get_json(silent=True) or {}
        crop = payload.get("crop", "").strip()
        quantity = payload.get("quantity", "").strip()
        gardener = payload.get("gardener", "").strip()
        location = payload.get("location", "").strip()

        if not crop or not quantity or not gardener:
            return jsonify({"error": "Champs manquants"}), 400

        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO harvests (crop, quantity, gardener, location) VALUES (?, ?, ?, ?)",
            (crop, quantity, gardener, location),
        )
        conn.commit()
        conn.close()
        return jsonify({"id": cursor.lastrowid, "crop": crop, "quantity": quantity, "gardener": gardener, "location": location}), 201

    @app.route("/api/harvests/<int:harvest_id>", methods=["PUT"])
    def update_harvest(harvest_id):
        conn = get_db_connection()
        conn.execute("UPDATE harvests SET distributed = 1 WHERE id = ?", (harvest_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Récolte marquée comme distribuée"}), 200

    @app.route("/api/weather/<city>")
    def get_weather(city):
        try:
            # Utilisation de l'API Open-Meteo (gratuite, pas de clé API requise)
            url = f"https://api.open-meteo.com/v1/forecast?latitude=48.8566&longitude=2.3522&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=auto"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                current = data.get("current", {})
                temp = current.get("temperature_2m", 20)
                humidity = current.get("relative_humidity_2m", 50)
                wind = current.get("wind_speed_10m", 10)
                weather_code = current.get("weather_code", 0)
                
                # Conversion du code météo en condition
                conditions = {
                    0: "Ensoleillé", 1: "Dégagé", 2: "Partiellement nuageux", 3: "Nuageux",
                    45: "Brouillard", 48: "Brouillard givrant", 51: "Bruine légère",
                    53: "Bruine modérée", 55: "Bruine dense", 61: "Pluie légère",
                    63: "Pluie modérée", 65: "Pluie forte", 71: "Neige légère",
                    73: "Neige modérée", 75: "Neige forte", 95: "Orage"
                }
                condition = conditions.get(weather_code, "Inconnu")
                
                # Génération de conseils automatisés
                advice = generate_gardening_advice(temp, humidity, condition)
                
                return jsonify({
                    "city": city,
                    "temperature": f"{temp}°C",
                    "humidity": f"{humidity}%",
                    "wind": f"{wind} km/h",
                    "condition": condition,
                    "advice": advice
                })
        except Exception as e:
            pass
        
        # Fallback vers les données statiques
        conn = get_db_connection()
        weather = conn.execute("SELECT * FROM weather_advice WHERE city = ? ORDER BY id DESC LIMIT 1", (city,)).fetchone()
        conn.close()
        if weather:
            return jsonify(dict(weather))
        return jsonify({"error": "Météo non disponible"}), 404

    return app


def generate_gardening_advice(temp, humidity, condition):
    """Génère des conseils de jardinage basés sur les conditions météo"""
    advice = []
    
    if temp > 30:
        advice.append("🔥 Canicule : Arrosez tôt le matin ou tard le soir. Ombragez les plants sensibles.")
    elif temp > 25:
        advice.append("☀️ Chaleur : Surveillez l'humidité du sol. Paillage recommandé.")
    elif temp < 5:
        advice.append("❄️ Gel : Protégez les plantes fragiles avec des voiles d'hivernage.")
    elif temp < 10:
        advice.append("🌡️ Frais : Évitez les semis sensibles au froid.")
    
    if humidity < 40:
        advice.append("💧 Sec : Arrosage régulier nécessaire.")
    elif humidity > 80:
        advice.append("💦 Humide : Surveillez les maladies fongiques, aérez les plants.")
    
    if "Pluie" in condition:
        advice.append("🌧️ Pluie : Réduisez l'arrosage. Bon moment pour planter.")
    elif "Soleil" in condition or "Ensoleillé" in condition:
        advice.append("☀️ Beau temps : Idéal pour récolter et travailler le sol.")
    elif "Orage" in condition:
        advice.append("⛈️ Orage : Rentrez les outils, protégez les jeunes plants.")
    
    return " ".join(advice) if advice else "Conditions favorables pour le jardinage."


app = create_app()
