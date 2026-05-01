from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from app.auth import login_required
from app.common.session_utils import current_user_id
from app.db import get_db
from app.services.semester_service import validate_semester_dates

bp = Blueprint("semesters", __name__)


def ensure_semester_columns(db):
    columns = [col["name"] for col in db.execute("PRAGMA table_info(semesters)").fetchall()]

    if "term" not in columns:
        db.execute("ALTER TABLE semesters ADD COLUMN term TEXT")

    if "year" not in columns:
        db.execute("ALTER TABLE semesters ADD COLUMN year INTEGER")

    db.commit()


def calculate_weeks(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    return max(1, (end - start).days // 7)


@bp.route("/semesters", methods=["GET"])
@login_required
def semesters():
    db = get_db()
    ensure_semester_columns(db)

    uid = current_user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    sems = db.execute(
        "SELECT * FROM semesters WHERE user_id = ? ORDER BY start_date DESC, id DESC",
        (uid,)
    ).fetchall()

    today = date.today().isoformat()

    current_semesters = []
    upcoming_semesters = []
    past_semesters = []
    active_id = None

    for sem in sems:
        if sem["start_date"] <= today <= sem["end_date"]:
            current_semesters.append(sem)
            active_id = sem["id"]
        elif sem["start_date"] > today:
            upcoming_semesters.append(sem)
        else:
            past_semesters.append(sem)

    return render_template(
        "semesters.html",
        semesters=sems,
        current_semesters=current_semesters,
        upcoming_semesters=upcoming_semesters,
        past_semesters=past_semesters,
        active_semester_id=active_id,
        profile=prof,
        today=today
    )


@bp.route("/semester/new", methods=["GET", "POST"])
@login_required
def semester_new():
    db = get_db()
    ensure_semester_columns(db)

    uid = current_user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    default_weeks = int(prof["default_semester_weeks"]) if prof else 16

    if request.method == "POST":
        term = (request.form.get("term") or "").strip()
        year = (request.form.get("year") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()

        if not term or not year:
            flash("Semester term and year are required.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        if not start_date or not end_date:
            flash("Start date and end date are required.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        _, _, date_error = validate_semester_dates(start_date, end_date)
        if date_error:
            flash(date_error)
            return render_template("semester_new.html", default_weeks=default_weeks)

        name = f"{term} {year}"
        weeks_i = calculate_weeks(start_date, end_date)

        db.execute(
            "INSERT INTO semesters (user_id, name, term, year, start_date, end_date, weeks) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uid, name, term, int(year), start_date, end_date, weeks_i),
        )
        db.commit()

        new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        session["active_semester_id"] = int(new_id)

        flash("Semester created.")
        return redirect(url_for("semesters.semesters"))

    return render_template("semester_new.html", default_weeks=default_weeks)


@bp.route("/semester/select/<int:semester_id>")
@login_required
def semester_select(semester_id: int):
    db = get_db()
    uid = current_user_id()

    row = db.execute(
        "SELECT id FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid)
    ).fetchone()

    if not row:
        flash("Semester not found.")
        return redirect(url_for("semesters.semesters"))

    session["active_semester_id"] = semester_id
    flash("Semester selected.")
    return redirect(url_for("dashboard.dashboard"))


@bp.route("/semester/edit/<int:semester_id>", methods=["GET", "POST"])
@login_required
def semester_edit(semester_id: int):
    db = get_db()
    ensure_semester_columns(db)

    uid = current_user_id()

    sem = db.execute(
        "SELECT * FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid),
    ).fetchone()

    if not sem:
        flash("Semester not found.")
        return redirect(url_for("semesters.semesters"))

    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    default_weeks = int(prof["default_semester_weeks"]) if prof else 16

    if request.method == "POST":
        term = (request.form.get("term") or "").strip()
        year = (request.form.get("year") or "").strip()
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()

        if not term or not year:
            flash("Semester term and year are required.")
            return render_template("semester_edit.html", semester=sem, default_weeks=default_weeks)

        if not start_date or not end_date:
            flash("Start date and end date are required.")
            return render_template("semester_edit.html", semester=sem, default_weeks=default_weeks)

        _, _, date_error = validate_semester_dates(start_date, end_date)
        if date_error:
            flash(date_error)
            return render_template("semester_edit.html", semester=sem, default_weeks=default_weeks)

        name = f"{term} {year}"
        weeks_i = calculate_weeks(start_date, end_date)

        db.execute(
            """
            UPDATE semesters
            SET name = ?, term = ?, year = ?, start_date = ?, end_date = ?, weeks = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, term, int(year), start_date, end_date, weeks_i, semester_id, uid),
        )
        db.commit()

        session["active_semester_id"] = semester_id
        flash("Semester updated.")
        return redirect(url_for("semesters.semesters"))

    return render_template("semester_edit.html", semester=sem, default_weeks=default_weeks)


@bp.route("/semester/delete/<int:semester_id>", methods=["POST"])
@login_required
def semester_delete(semester_id: int):
    db = get_db()
    uid = current_user_id()

    db.execute(
        "DELETE FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid),
    )
    db.commit()

    if session.get("active_semester_id") == semester_id:
        session.pop("active_semester_id", None)

    flash("Semester deleted.")
    return redirect(url_for("semesters.semesters"))