from __future__ import annotations
from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import get_db
from .auth import login_required
from .pacing import compute_pace, safe_to_spend, runout_week_projection

bp = Blueprint("core", __name__, url_prefix="")


def _user_id() -> int:
    return int(session["user_id"])


def _active_semester_id() -> int | None:
    sid = session.get("active_semester_id")
    return int(sid) if sid is not None else None


def _cents_to_money(cents: int) -> float:
    return (cents or 0) / 100.0


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    uid = _user_id()
    sid = _active_semester_id()

    prof = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (uid,),
    ).fetchone()

    today = date.today().isoformat()

    if sid is None:
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
            sem = db.execute(
                """
                SELECT *
                FROM semesters
                WHERE user_id = ?
                ORDER BY date(start_date) DESC, id DESC
                LIMIT 1
                """,
                (uid,),
            ).fetchone()

        if sem is None:
            return render_template(
                "dashboard_empty.html",
                semesters=[],
                profile=prof,
            )

        sid = int(sem["id"])
        session["active_semester_id"] = sid

    sem = db.execute(
        "SELECT * FROM semesters WHERE id = ? AND user_id = ?",
        (sid, uid),
    ).fetchone()

    if not sem:
        session.pop("active_semester_id", None)
        flash("Active semester not found.")
        return redirect(url_for("semesters.semesters"))

    aid_total_cents = db.execute(
        """
        SELECT COALESCE(SUM(amount_cents), 0)
        FROM aid_awards
        WHERE semester_id = ?
        """,
        (sid,),
    ).fetchone()[0]

    income_total_cents = db.execute(
        """
        SELECT COALESCE(SUM(amount_cents), 0)
        FROM transactions
        WHERE semester_id = ?
          AND user_id = ?
          AND type = 'income'
        """,
        (sid, uid),
    ).fetchone()[0]

    expense_total_cents = db.execute(
        """
        SELECT COALESCE(SUM(amount_cents), 0)
        FROM transactions
        WHERE semester_id = ?
          AND user_id = ?
          AND type = 'expense'
        """,
        (sid, uid),
    ).fetchone()[0]

    total_funds_cents = int(aid_total_cents) + int(income_total_cents)
    spent_cents = int(expense_total_cents)

    total_funds = _cents_to_money(total_funds_cents)
    spent = _cents_to_money(spent_cents)
    remaining = max(0.0, total_funds - spent)

    pace = compute_pace(
        start_iso=sem["start_date"],
        end_iso=sem["end_date"],
        weeks_total=int(sem["weeks"]),
        today=date.today(),
        funds_spent=spent,
        total_funds=total_funds,
    )

    safe_weekly = safe_to_spend(
        remaining,
        pace.week_now,
        pace.weeks_total,
    )

    alerts = []
    if total_funds > 0:
        if pace.funds_spent_pct >= 100:
            alerts.append("You’ve reached 100% of your funds.")
        elif pace.funds_spent_pct >= 90:
            alerts.append("You’ve used 90% of your funds.")
        elif pace.funds_spent_pct >= 75:
            alerts.append("You’ve used 75% of your funds.")

    cat_rows = db.execute(
        """
        SELECT
            c.name AS category,
            COALESCE(SUM(t.amount_cents), 0) AS total_cents
        FROM categories c
        LEFT JOIN transactions t
          ON t.category_id = c.id
         AND t.type = 'expense'
         AND t.semester_id = ?
         AND t.user_id = ?
        WHERE c.user_id = ?
        GROUP BY c.id
        HAVING total_cents > 0
        ORDER BY total_cents DESC
        """,
        (sid, uid, uid),
    ).fetchall()

    proj = runout_week_projection(
        remaining=remaining,
        spent_so_far=spent,
        week_now=pace.week_now,
    )

    recent = db.execute(
        """
        SELECT t.*, COALESCE(c.name, '') AS category_name
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        WHERE t.user_id = ?
          AND t.semester_id = ?
        ORDER BY t.date DESC, t.id DESC
        LIMIT 10
        """,
        (uid, sid),
    ).fetchall()

    aid_list = db.execute(
        """
        SELECT *
        FROM aid_awards
        WHERE semester_id = ?
        ORDER BY disbursement_date DESC, id DESC
        """,
        (sid,),
    ).fetchall()

    return render_template(
        "dashboard.html",
        profile=prof,
        semester=sem,
        pace=pace,
        total_funds=total_funds,
        spent=spent,
        remaining=remaining,
        safe_weekly=safe_weekly,
        alerts=alerts,
        categories=cat_rows,
        projection_week=proj,
        recent=recent,
        aid_list=aid_list,
    )