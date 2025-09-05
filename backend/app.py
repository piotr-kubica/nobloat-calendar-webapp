import bcrypt
import sqlite3
import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask import session
from functools import wraps
from datetime import timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")
app.permanent_session_lifetime = timedelta(days=7)
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",   # same-site requests (subdomains count as same-site)
    SESSION_COOKIE_SECURE=True,      # only send over HTTPS (Cloudflare edge is HTTPS)
    SESSION_COOKIE_DOMAIN=os.environ.get("COOKIE_DOMAIN", ".yourdomain.com")  # share cookie across subdomains (optional but useful)
)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
CORS(app, supports_credentials=True, origins=os.getenv("DOMAIN_ORIGINS", "").split(","))  # "https://yourdomain.com"

# Keep failed attempts in memory (for rate-limiting)
FAILED_LOGINS = {}

# Ensure the data directory exists
DB_DIR = "data"
DB = os.path.join(DB_DIR, "activities.db")


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)

        # Only initialize if DB doesn't exist
    if not os.path.exists(DB):
        print("Database not found. Creating training.db...")

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()

            # Users table
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
            """)

            # Activities table
            c.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT CHECK(type IN ('meeting', 'event', 'sport', 'note')) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    user_id INTEGER,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)

            conn.commit()

            sql_create_user("demosuer", "nobloat", conn)


def sql_create_user(username, password, connection):
    # Create demo user if not exists
    c = connection.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not c.fetchone():
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
            c.commit()
            return True
        return False
    except sqlite3.IntegrityError:
        return False


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return "Unauthorized", 401
        return f(*args, **kwargs)
    return wrapped


@app.route("/api/session")
def get_session():
    # changed: read the same key that login() sets
    username = session.get("username")
    if username:
        return jsonify({"logged_in": True, "username": username})
    return jsonify({"logged_in": False}), 200


@app.route("/api/activities/<year_month>", methods=["GET"])
@login_required
def get_activities_by_month(year_month):
    # Expect format: YYYY-MM
    like_pattern = f"{year_month}-%"
    user_id = session.get("user_id")
    with sqlite3.connect(DB) as conn:
        rows = conn.execute("""
            SELECT id, date, type, title, description
            FROM activities
            WHERE date LIKE ? AND user_id = ?
        """, (like_pattern, user_id)).fetchall()
        
        result = {}
        for row in rows:
            date = row[1]
            activity = {
                "id": row[0],
                "type": row[2],
                "title": row[3],
                "description": row[4] or ""
            }
            result.setdefault(date, []).append(activity)

        return jsonify(result)

@app.route("/api/activities", methods=["POST"])
@login_required
def add_activity():
    data = request.get_json()
    date = data.get("date")
    type_ = data.get("type")
    title = data.get("title")
    description = (data.get("description") or "")[:255]

    if not (date and type_ and title):
        return "Missing fields", 400

    if type_ not in ['meeting', 'event', 'sport', 'note']:
        return "Invalid activity type", 400

    with sqlite3.connect(DB) as conn:
        # use the authenticated user's id from session
        user_id = session.get("user_id")
        if not user_id:
            return "Unauthorized", 401

        conn.execute("""
            INSERT INTO activities (date, type, title, description, user_id)
            VALUES (?, ?, ?, ?, ?)
        """, (date, type_, title, description, user_id))
        conn.commit()

    return "Created", 201

@app.route("/api/activities/<int:activity_id>", methods=["DELETE"])
@login_required
def delete_activity(activity_id):
    with sqlite3.connect(DB) as conn:
        conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
    return "Deleted", 200


@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return "Missing credentials", 400

    # Rate limiting: simple delay after 5 failed attempts
    attempts = FAILED_LOGINS.get(username, 0)
    if attempts >= 10:
        return "Too many failed attempts. Try again later.", 429

    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        if row is None:
            FAILED_LOGINS[username] = attempts + 1
            return "Invalid credentials", 401

        user_id, stored_hash = row
        if not bcrypt.checkpw(password.encode(), stored_hash):
            FAILED_LOGINS[username] = attempts + 1
            return "Invalid credentials", 401

        # Clear failed attempts on successful login
        FAILED_LOGINS[username] = 0

        # Store session
        session['user_id'] = user_id
        session['username'] = username
        session['permanent'] = True

        return jsonify({"message": "Logged in", "user": username})


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    # clear server-side session
    session.pop('user_id', None)
    session.pop('username', None)
    session.clear()

    # build response and instruct browser to remove the cookie
    cookie_name = app.config.get("SESSION_COOKIE_NAME", "session")
    resp = jsonify({"message": "Logged out"})

    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"

    # prefer delete_cookie (works across Flask versions)
    resp.delete_cookie(
        cookie_name,
        path=app.config.get("SESSION_COOKIE_PATH", "/"),
        domain=app.config.get("SESSION_COOKIE_DOMAIN")
    )
    return resp, 200


@app.route("/")
def serve_index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    init_db()
    # app.run(debug=True, host="0.0.0.0", port=5000)
    app.run(debug=False, host="0.0.0.0", port=5000)
