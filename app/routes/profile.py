from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.session_utils import current_user_id
from app.db import get_db

bp = Blueprint("profile", __name__)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    uid = current_user_id()
    row = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    if request.method == "POST":
        display_name = (request.form.get("display_name") or "").strip()
        school = (request.form.get("school") or "").strip()
        weeks = request.form.get("default_semester_weeks") or "16"
        try:
            weeks_i = int(weeks)
        except Exception:
            weeks_i = 16

        if weeks_i < 8 or weeks_i > 26:
            flash("Default semester weeks must be between 8 and 26.")
            return render_template("profile.html", profile=row)

        db.execute(
            "INSERT INTO profiles (user_id, display_name, school, default_semester_weeks) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name, school=excluded.school, default_semester_weeks=excluded.default_semester_weeks",
            (uid, display_name, school, weeks_i),
        )
        db.commit()
        flash("Profile saved.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("profile.html", profile=row)
