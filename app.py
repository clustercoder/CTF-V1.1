# app.py — cleaned version
import os
import hmac
import hashlib
import secrets
from datetime import datetime
from sqlalchemy import func, desc
import docker
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis

# ------------------ CONFIG ------------------
app = Flask(__name__)

# Use REDIS_URL env var (defaults to local redis used in docker-compose)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
# Create a redis client only if you want to use it (optional)
try:
    redis_client = Redis.from_url(REDIS_URL)
except Exception:
    redis_client = None

# Secrets / DB / proxy defaults
FLAG_SECRET = os.getenv("FLAG_SECRET", "dev_secret").encode()
FLASK_SECRET = os.getenv("FLASK_SECRET", "dev_flask_secret")
# IMPORTANT: set PROXY_HOST to your host machine's IP that participants will reach (see README below)
PROXY_HOST = os.getenv("PROXY_HOST", "host.docker.internal")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/ctf")

app.secret_key = FLASK_SECRET
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

MAX_ATTEMPTS_PER_CHALLENGE = 30

# ------------------ RATE LIMITER ------------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=REDIS_URL
)

# ------------------ DOCKER ------------------
def get_docker_client():
    try:
        return docker.from_env()
    except Exception as e:
        print(f"⚠ Docker unavailable: {e}")
        return None

# ------------------ MODELS ------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    last_login_token = db.Column(db.String(32), nullable=True)
    solves = db.relationship("Solve", backref="user", lazy=True)
    attempts = db.relationship("Attempt", backref="user", lazy=True)

class Challenge(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    flag_hash = db.Column(db.String(64), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    docker_image = db.Column(db.String(120), nullable=True)
    port = db.Column(db.Integer, nullable=True)

class Solve(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.String(80), db.ForeignKey("challenge.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Attempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.String(80), db.ForeignKey("challenge.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    chal_id = db.Column(db.String(80), db.ForeignKey("challenge.id"), nullable=False)
    container_id = db.Column(db.String(120), nullable=False)
    host_port = db.Column(db.Integer, nullable=False)

# ------------------ LOGIN MANAGER ------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def enforce_single_session():
    if current_user.is_authenticated:
        token = session.get("login_token")
        if not token or token != current_user.last_login_token:
            logout_user()
            flash("You have been logged out because your account was used elsewhere.", "danger")
            return redirect(url_for("login"))

# ------------------ FLAG HASH ------------------
def hash_flag(flag: str) -> str:
    return hmac.new(FLAG_SECRET, flag.encode(), hashlib.sha256).hexdigest()

# ------------------ ROUTES ------------------
@app.route("/")
def index():
    challenges = Challenge.query.all()
    return render_template("index.html", challenges=challenges)

@app.route("/challenge/<challenge_id>", methods=["GET", "POST"])
@login_required
def challenge(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)

    if request.method == "POST":
        attempts_count = Attempt.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).count()
        if attempts_count >= MAX_ATTEMPTS_PER_CHALLENGE:
            flash(f"Max attempts ({MAX_ATTEMPTS_PER_CHALLENGE}) reached.", "danger")
            return redirect(url_for("challenge", challenge_id=challenge_id))

        submitted_flag = request.form.get("flag", "")
        attempt_hash = hmac.new(FLAG_SECRET, submitted_flag.encode(), hashlib.sha256).hexdigest()

        new_attempt = Attempt(user_id=current_user.id, challenge_id=challenge.id)
        db.session.add(new_attempt)
        db.session.commit()

        if hmac.compare_digest(attempt_hash, challenge.flag_hash):
            if not Solve.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
                solve = Solve(user_id=current_user.id, challenge_id=challenge.id)
                db.session.add(solve)
                db.session.commit()
            flash("Correct flag!", "success")
        else:
            flash("Wrong flag!", "danger")

        return redirect(url_for("challenge", challenge_id=challenge_id))

    return render_template("challenge.html", challenge=challenge)

# ------------------ INSTANCE MANAGEMENT ------------------
@app.route("/launch/<challenge_id>")
@login_required
@limiter.limit("7 per minute")
def launch(challenge_id):
    challenge = Challenge.query.get_or_404(challenge_id)
    client = get_docker_client()
    if not client:
        return jsonify({"error": "Docker unavailable"}), 500

    existing = Instance.query.filter_by(user_id=current_user.id, chal_id=challenge_id).first()
    if existing:
        try:
            client.containers.get(existing.container_id)
            return jsonify({"url": f"/instance/{existing.host_port}/"})
        except docker.errors.NotFound:
            db.session.delete(existing)
            db.session.commit()

    if not challenge.docker_image:
        return jsonify({"error": "This challenge has no instance."}), 400

    container = client.containers.run(
        challenge.docker_image,
        detach=True,
        ports={f"{challenge.port}/tcp": None},
        mem_limit="256m",
        network="bridge"
    )

    container.reload()
    host_port = int(container.ports[f"{challenge.port}/tcp"][0]["HostPort"])

    inst = Instance(
        user_id=current_user.id,
        chal_id=challenge_id,
        container_id=container.id,
        host_port=host_port
    )
    db.session.add(inst)
    db.session.commit()

    return jsonify({"url": f"/instance/{host_port}/"})

@app.route("/instance/<int:port>/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/instance/<int:port>/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
def proxy_instance(port, path):
    instance = Instance.query.filter_by(host_port=port, user_id=current_user.id).first()
    if not instance:
        if Instance.query.filter_by(host_port=port).first():
            return "You do not have permission to access this instance.", 403
        return "Instance not found or has been stopped.", 404

    url = f"http://{PROXY_HOST}:{port}/{path}"
    if request.query_string:
        url += '?' + request.query_string.decode('utf-8')

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=10
        )
    except requests.exceptions.ConnectionError:
        return "Failed to connect to the challenge instance. It might be stopped or still starting up.", 503

    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    headers = [(n, v) for (n, v) in resp.headers.items() if n.lower() not in excluded]

    return Response(resp.iter_content(chunk_size=8192), status=resp.status_code, headers=dict(headers))

# ------------------ SCOREBOARD ------------------
@app.route("/scoreboard")
def show_scoreboard():
    scoreboard_data = db.session.query(
        User.username,
        func.count(Solve.id).label("solves_count"),
        func.coalesce(func.sum(Challenge.points), 0).label("total_points")
    ).outerjoin(Solve, User.id == Solve.user_id)\
     .outerjoin(Challenge, Solve.challenge_id == Challenge.id)\
     .group_by(User.id, User.username)\
     .order_by(desc("total_points"), desc("solves_count"))\
     .all()

    return render_template("scoreboard.html", rows=scoreboard_data)

# ------------------ AUTH ------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("register"))

        hashed = generate_password_hash(password)
        user = User(username=username, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account created, please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            token = secrets.token_hex(16)
            user.last_login_token = token
            db.session.commit()
            login_user(user)
            session["login_token"] = token
            flash("Logged in!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("login"))

# ------------------ RUN ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000, debug=False)
