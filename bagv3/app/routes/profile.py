from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.constants import US_STATE_ABBREVIATIONS
from app.common.session_utils import current_user_id
from app.db import get_db

bp = Blueprint("profile", __name__)


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    uid = current_user_id()

    row = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (uid,)
    ).fetchone()

    if request.method == "POST":
        display_name = (request.form.get("display_name") or "").strip()
        state = (request.form.get("state") or "").strip()
        school = (request.form.get("school") or "").strip()
        student_status = (request.form.get("student_status") or "").strip()
        profile_image = (request.form.get("profile_image") or "").strip()
        weeks = request.form.get("default_semester_weeks") or "16"

        try:
            weeks_i = int(weeks)
        except Exception:
            weeks_i = 16

        if weeks_i < 8 or weeks_i > 26:
            flash("Default semester weeks must be between 8 and 26.")
            return render_template(
                "profile.html",
                profile=row,
                states=US_STATE_ABBREVIATIONS,
            )

        if student_status not in ("", "Full-time", "Part-time"):
            flash("Please choose a valid student status.")
            return render_template(
                "profile.html",
                profile=row,
                states=US_STATE_ABBREVIATIONS,
            )

        allowed_images = {
            "baglogo.png",
            "baglogogreen.png",
            "baglogored.png",
            "baglogopurple.png",
            "",
        }
        if profile_image not in allowed_images:
            profile_image = ""

        db.execute(
            """
            INSERT INTO profiles (
                user_id,
                display_name,
                state,
                school,
                student_status,
                profile_image,
                default_semester_weeks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                display_name = excluded.display_name,
                state = excluded.state,
                school = excluded.school,
                student_status = excluded.student_status,
                profile_image = excluded.profile_image,
                default_semester_weeks = excluded.default_semester_weeks
            """,
            (uid, display_name, state, school, student_status, profile_image, weeks_i),
        )
        db.commit()

        flash("Profile saved.")
        return redirect(url_for("profile.profile"))

    return render_template(
        "profile.html",
        profile=row,
        states=US_STATE_ABBREVIATIONS,
    )