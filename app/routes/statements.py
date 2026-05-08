# BAG — Budgeting Aid Guide
# Copyright © 2026 Group_0
# All Rights Reserved

from flask import Blueprint, render_template, session, redirect, url_for
from app.db import get_db

bp = Blueprint("statements", __name__, url_prefix="/statements")


@bp.route("/")
def statements():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_db()
    user_id = session["user_id"]

    transactions = db.execute(
        """
        SELECT 
            t.id,
            t.date,
            t.note,
            t.amount_cents,
            'expense' AS entry_type,
            c.name AS category_name,
            s.name AS semester_name
        FROM transactions t
        LEFT JOIN categories c ON t.category_id = c.id
        LEFT JOIN semesters s ON t.semester_id = s.id
        WHERE t.user_id = ?

        UNION ALL

        SELECT 
            a.id,
            a.disbursement_date AS date,
            a.label AS note,
            a.amount_cents,
            'income' AS entry_type,
            a.source_type AS category_name,
            s.name AS semester_name
        FROM aid_awards a
        LEFT JOIN semesters s ON a.semester_id = s.id
        WHERE s.user_id = ?

        ORDER BY date DESC
        """,
        (user_id, user_id),
    ).fetchall()

    return render_template("statements.html", transactions=transactions)
