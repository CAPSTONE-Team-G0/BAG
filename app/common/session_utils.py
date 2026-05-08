# BAG — Budgeting Aid Guide
# Copyright © 2026 Group_0
# All Rights Reserved
from datetime import date
from flask import session
from app.db import get_db


def current_user_id() -> int:
    return int(session["user_id"])


def active_semester_id() -> int | None:
    db = get_db()
    uid = current_user_id()

    today = date.today().isoformat()

    sem = db.execute(
        """
        SELECT id
        FROM semesters
        WHERE user_id = ?
          AND date(start_date) <= date(?)
          AND date(end_date) >= date(?)
        ORDER BY date(start_date) DESC
        LIMIT 1
        """,
        (uid, today, today),
    ).fetchone()

    return int(sem["id"]) if sem else None
