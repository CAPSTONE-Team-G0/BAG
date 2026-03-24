from flask import Blueprint, redirect, session, url_for

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    if session.get("user_id") is None:
        return redirect(url_for("auth.login"))
    return redirect(url_for("dashboard.dashboard"))
