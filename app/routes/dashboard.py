# BAG — Budgeting Aid Guide
# Copyright © 2026 Group_0
# All Rights Reserved

from datetime import date
from flask import Blueprint, render_template
from app.auth import login_required, student_required
from app.common.session_utils import current_user_id
from app.db import get_db
from app.services.dashboard_service import load_dashboard_data

bp = Blueprint("dashboard", __name__)


@bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    db = get_db()
    uid = current_user_id()

    prof = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (uid,),
    ).fetchone()

    today = date.today().isoformat()

    sem = db.execute(
        """
        SELECT *
        FROM semesters
        WHERE user_id = ?
          AND date(start_date) <= date(?)
          AND date(end_date) >= date(?)
        ORDER BY date(start_date) DESC, id DESC
        LIMIT 1
        """,
        (uid, today, today),
    ).fetchone()

    if sem is None:
        return render_template("dashboard_empty.html", profile=prof)

    sid = int(sem["id"])
    data = load_dashboard_data(db, uid, sid, sem)

    semester_percent = data.get("semester_percent", 0)
    funds_percent = data.get("funds_percent", 0)

    return render_template(
        "dashboard.html",
        profile=prof,
        semester=sem,
        semester_percent=semester_percent,
        funds_percent=funds_percent,
        **data
    )
