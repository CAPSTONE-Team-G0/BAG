from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from .email_utils import send_reset_email
from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def student_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("auth.login"))

        if session.get("user_role") != "student":
            flash("Access denied.")
            return redirect(url_for("parent_access.parent_access"))

        return view(*args, **kwargs)

    return wrapped


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        role = (request.form.get("role") or "student").strip().lower()

        if not email:
            flash("Email is required.")
            return render_template("register.html")

        if not password or len(password) < 6:
            flash("Password is required (min 6 characters).")
            return render_template("register.html")

        if role not in ("student", "parent"):
            flash("Please select a valid account type.")
            return render_template("register.html")

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            flash("That email is already registered. Please log in.")
            return redirect(url_for("auth.login"))

        db.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
            (email, generate_password_hash(password), role),
        )
        db.commit()

        flash("Account created. Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["user_role"] = user["role"]

        flash("Welcome back.")

        if user["role"] == "parent":
            return redirect(url_for("parent_access.parent_access"))

        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html")


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset")


def verify_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset", max_age=expiration)
    except Exception:
        return None
    return email

@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user:
            token = generate_reset_token(email)

            reset_url = url_for(
                "auth.reset_password",
                token=token,
                _external=True
            )

            # ✅ send email
            send_reset_email(email, reset_url)

            print("Reset link:", reset_url)  # debug

        flash("If that email exists, a reset link has been sent.")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html")


# ---------------------------
# Reset Password
# ---------------------------
@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token)

    if email is None:
        flash("Invalid or expired reset link.")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        password = request.form.get("password") or ""

        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return render_template("reset_password.html")

        db = get_db()

        db.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (generate_password_hash(password), email),
        )
        db.commit()

        flash("Password updated. Please log in.")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for("auth.login"))