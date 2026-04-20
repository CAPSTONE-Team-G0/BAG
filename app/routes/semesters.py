from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.auth import login_required
from app.common.session_utils import current_user_id
from app.db import get_db
from app.services.semester_service import normalize_weeks, validate_semester_dates

bp = Blueprint("semesters", __name__)


@bp.route("/semesters", methods=["GET"])
@login_required
def semesters():
    db = get_db()
    uid = current_user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    sems = db.execute(
        "SELECT * FROM semesters WHERE user_id = ?",
        (uid,)
    ).fetchall()

    today = date.today().isoformat()
    active_id = None

    for sem in sems:
        if sem["start_date"] <= today <= sem["end_date"]:
            active_id = sem["id"]
            break

    return render_template(
        "semesters.html",
        semesters=sems,
        active_semester_id=active_id,
        profile=prof,
        today=today
    )


@bp.route("/semester/new", methods=["GET", "POST"])
@login_required
def semester_new():
    db = get_db()
    uid = current_user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    default_weeks = int(prof["default_semester_weeks"]) if prof else 16

    if request.method == "POST":
        name = (request.form.get("name") or "").strip() or "My Semester"
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()
        weeks_raw = request.form.get("weeks") or str(default_weeks)

        if not start_date or not end_date:
            flash("Start date and end date are required.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        _, _, date_error = validate_semester_dates(start_date, end_date)
        if date_error:
            flash(date_error)
            return render_template("semester_new.html", default_weeks=default_weeks)

        weeks_i, week_error = normalize_weeks(weeks_raw, default_weeks)
        if week_error:
            flash(week_error)
            return render_template("semester_new.html", default_weeks=default_weeks)

        db.execute(
            "INSERT INTO semesters (user_id, name, start_date, end_date, weeks) VALUES (?, ?, ?, ?, ?)",
            (uid, name, start_date, end_date, weeks_i),
        )
        db.commit()

        new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        session["active_semester_id"] = int(new_id)

        flash("Semester created and selected.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("semester_new.html", default_weeks=default_weeks)


@bp.route("/semester/select/<int:semester_id>")
@login_required
def semester_select(semester_id: int):
    db = get_db()
    uid = current_user_id()
    row = db.execute("SELECT id FROM semesters WHERE id = ? AND user_id = ?", (semester_id, uid)).fetchone()
    if not row:
        flash("Semester not found.")
        return redirect(url_for("semesters.semesters"))
    session["active_semester_id"] = semester_id
    flash("Semester selected.")
    return redirect(url_for("dashboard.dashboard"))