from flask import Blueprint, flash, redirect, render_template, session, url_for
from app.auth import login_required, student_required
from app.common.session_utils import active_semester_id, current_user_id
from app.db import get_db
from app.services.dashboard_service import load_dashboard_data

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    db = get_db()
    uid = current_user_id()
    sid = active_semester_id()

    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    if sid is None:
        sems = db.execute("SELECT * FROM semesters WHERE user_id = ? ORDER BY created_at DESC", (uid,)).fetchall()
        return render_template("dashboard_empty.html", semesters=sems, profile=prof)

    sem = db.execute("SELECT * FROM semesters WHERE id = ? AND user_id = ?", (sid, uid)).fetchone()
    if not sem:
        session.pop("active_semester_id", None)
        flash("Active semester not found. Please select a semester.")
        return redirect(url_for("semesters.semesters"))

    data = load_dashboard_data(db, uid, sid, sem)
    return render_template("dashboard.html", profile=prof, semester=sem, **data)
