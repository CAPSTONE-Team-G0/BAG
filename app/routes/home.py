from flask import Blueprint, render_template, redirect, session, url_for
from app.db import get_db
from app.auth import login_required

bp = Blueprint("home", __name__)


@bp.route("/")
def home():
    return render_template("intro_pages/index.html")

@bp.route("/about")
def about():
    return render_template("intro_pages/about.html")


@bp.route("/welcome")
@login_required
def welcome():
    db = get_db()
    uid = session["user_id"]

    profile_done = db.execute(
        """
        SELECT user_id
        FROM profiles
        WHERE user_id = ?
          AND display_name IS NOT NULL
          AND display_name != ''
        """,
        (uid,)
    ).fetchone() is not None

    semester_done = db.execute(
        "SELECT id FROM semesters WHERE user_id = ? LIMIT 1",
        (uid,)
    ).fetchone() is not None

    funds_done = db.execute(
        """
        SELECT a.id
        FROM aid_awards a
        JOIN semesters s ON s.id = a.semester_id
        WHERE s.user_id = ?
        LIMIT 1
        """,
        (uid,)
    ).fetchone() is not None

    expense_done = db.execute(
        """
        SELECT id
        FROM transactions
        WHERE user_id = ?
          AND type = 'expense'
        LIMIT 1
        """,
        (uid,)
    ).fetchone() is not None

    goal_done = db.execute(
        """
        SELECT id
        FROM budget_goals
        WHERE user_id = ?
          AND is_active = 1
        LIMIT 1
        """,
        (uid,)
    ).fetchone() is not None

    parent_done = db.execute(
        """
        SELECT id
        FROM parent_links
        WHERE student_user_id = ?
        LIMIT 1
        """,
        (uid,)
    ).fetchone() is not None

    return render_template(
        "welcome.html",
        profile_done=profile_done,
        semester_done=semester_done,
        funds_done=funds_done,
        expense_done=expense_done,
        goal_done=goal_done,
        parent_done=parent_done,
    )