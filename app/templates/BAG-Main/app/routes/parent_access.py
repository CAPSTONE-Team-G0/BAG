from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.auth import login_required
from app.common.session_utils import current_user_id
from app.db import get_db
from app.services.dashboard_service import load_dashboard_data

bp = Blueprint("parent_access", __name__)


@bp.route("/parent-access", methods=["GET", "POST"])
@login_required
def parent_access():
    db = get_db()
    student_id = current_user_id()

    if request.method == "POST":
        action = request.form.get("action", "").strip()

        if action == "add":
            parent_email = (request.form.get("parent_email") or "").strip().lower()

            if not parent_email:
                flash("Parent email is required.")
                return redirect(url_for("parent_access.parent_access"))

            parent_user = db.execute(
                "SELECT id, email FROM users WHERE email = ?",
                (parent_email,),
            ).fetchone()

            if not parent_user:
                flash("That parent account does not exist yet. They need to register first.")
                return redirect(url_for("parent_access.parent_access"))

            if parent_user["id"] == student_id:
                flash("You cannot link your own account as a parent viewer.")
                return redirect(url_for("parent_access.parent_access"))

            can_view_on_track = 1 if request.form.get("can_view_on_track") else 0
            can_view_remaining_funding = 1 if request.form.get("can_view_remaining_funding") else 0
            can_view_total_funds = 1 if request.form.get("can_view_total_funds") else 0
            can_view_spending_breakdown = 1 if request.form.get("can_view_spending_breakdown") else 0

            db.execute(
                """
                INSERT INTO parent_links (
                    student_user_id,
                    parent_user_id,
                    can_view_on_track,
                    can_view_remaining_funding,
                    can_view_total_funds,
                    can_view_spending_breakdown
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_user_id, parent_user_id)
                DO UPDATE SET
                    can_view_on_track=excluded.can_view_on_track,
                    can_view_remaining_funding=excluded.can_view_remaining_funding,
                    can_view_total_funds=excluded.can_view_total_funds,
                    can_view_spending_breakdown=excluded.can_view_spending_breakdown
                """,
                (
                    student_id,
                    parent_user["id"],
                    can_view_on_track,
                    can_view_remaining_funding,
                    can_view_total_funds,
                    can_view_spending_breakdown,
                ),
            )
            db.commit()
            flash("Parent access saved.")
            return redirect(url_for("parent_access.parent_access"))

        elif action == "remove":
            link_id = request.form.get("link_id")

            db.execute(
                "DELETE FROM parent_links WHERE id = ? AND student_user_id = ?",
                (link_id, student_id),
            )
            db.commit()
            flash("Parent access removed.")
            return redirect(url_for("parent_access.parent_access"))

    linked_parents = db.execute(
        """
        SELECT
            pl.*,
            u.email AS parent_email
        FROM parent_links pl
        JOIN users u ON u.id = pl.parent_user_id
        WHERE pl.student_user_id = ?
        ORDER BY u.email
        """,
        (student_id,),
    ).fetchall()

    parent_views = db.execute(
        """
        SELECT
            pl.*,
            u.email AS student_email,
            p.display_name AS student_name
        FROM parent_links pl
        JOIN users u ON u.id = pl.student_user_id
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE pl.parent_user_id = ?
        ORDER BY u.email
        """,
        (student_id,),
    ).fetchall()

    return render_template(
        "parent_access.html",
        linked_parents=linked_parents,
        parent_views=parent_views,
    )


@bp.route("/parent-view/<int:student_id>")
@login_required
def parent_view(student_id: int):
    db = get_db()
    parent_id = current_user_id()

    link = db.execute(
        """
        SELECT
            pl.*,
            u.email AS student_email,
            p.display_name AS student_name
        FROM parent_links pl
        JOIN users u ON u.id = pl.student_user_id
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE pl.student_user_id = ? AND pl.parent_user_id = ?
        """,
        (student_id, parent_id),
    ).fetchone()

    if not link:
        flash("You do not have permission to view that student.")
        return redirect(url_for("parent_access.parent_access"))

    profile = db.execute(
        "SELECT * FROM profiles WHERE user_id = ?",
        (student_id,),
    ).fetchone()

    semester = db.execute(
        """
        SELECT *
        FROM semesters
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (student_id,),
    ).fetchone()

    if not semester:
        flash("That student does not have a semester set up yet.")
        return redirect(url_for("parent_access.parent_access"))

    data = load_dashboard_data(db, student_id, semester["id"], semester)

    return render_template(
        "parent_dashboard.html",
        student_profile=profile,
        student_email=link["student_email"],
        student_name=link["student_name"],
        semester=semester,
        link=link,
        pace=data["pace"],
        total_funds=data["total_funds"],
        spent=data["spent"],
        remaining=data["remaining"],
        safe_weekly=data["safe_weekly"],
        alerts=data["alerts"],
        categories=data["categories"],
        projection_week=data["projection_week"],
        recent=data["recent"],
        aid_list=data["aid_list"],
    )