from datetime import date, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.money import money_to_cents
from app.common.session_utils import active_semester_id, current_user_id
from app.db import get_db
from app.services.category_service import ensure_default_categories

bp = Blueprint("categories", __name__)


def _goal_date_range(duration: str, semester_row=None):
    today = date.today()

    if duration == "weekly":
        start_date = today
        end_date = today + timedelta(days=6)
    elif duration == "monthly":
        start_date = today
        end_date = today + timedelta(days=29)
    elif duration == "semester":
        if semester_row:
            start_date = date.fromisoformat(semester_row["start_date"])
            end_date = date.fromisoformat(semester_row["end_date"])
        else:
            start_date = today
            end_date = today + timedelta(days=111)
    else:
        return None, None

    return start_date.isoformat(), end_date.isoformat()


@bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    db = get_db()
    uid = current_user_id()
    sid = active_semester_id()

    ensure_default_categories(db, uid)

    semester = None
    if sid is not None:
        semester = db.execute(
            """
            SELECT *
            FROM semesters
            WHERE id = ? AND user_id = ?
            """,
            (sid, uid),
        ).fetchone()

    if semester is None:
        semester = db.execute(
            """
            SELECT *
            FROM semesters
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (uid,),
        ).fetchone()
        if semester:
            sid = semester["id"]

    if request.method == "POST":
        category_id = (request.form.get("category_id") or "").strip()
        goal_amount = (request.form.get("goal_amount") or "").strip()
        duration = (request.form.get("duration") or "").strip().lower()

        if not sid:
            flash("Please select an active semester before creating budget goals.")
            return redirect(url_for("categories.categories"))

        if not category_id:
            flash("Please choose a category.")
            return redirect(url_for("categories.categories"))

        if duration not in {"weekly", "monthly", "semester"}:
            flash("Please choose a valid duration.")
            return redirect(url_for("categories.categories"))

        goal_cents = money_to_cents(goal_amount)
        if goal_cents is None or goal_cents <= 0:
            flash("Enter a valid goal amount.")
            return redirect(url_for("categories.categories"))

        try:
            cid = int(category_id)
        except ValueError:
            flash("Invalid category.")
            return redirect(url_for("categories.categories"))

        category = db.execute(
            """
            SELECT id, name
            FROM categories
            WHERE id = ? AND user_id = ?
            """,
            (cid, uid),
        ).fetchone()

        if not category:
            flash("Category not found.")
            return redirect(url_for("categories.categories"))

        start_date, end_date = _goal_date_range(duration, semester)
        if not start_date or not end_date:
            flash("Could not create that goal.")
            return redirect(url_for("categories.categories"))

        existing_goal = db.execute(
            """
            SELECT id
            FROM budget_goals
            WHERE user_id = ?
              AND semester_id = ?
              AND category_id = ?
              AND duration = ?
              AND is_active = 1
            """,
            (uid, sid, cid, duration),
        ).fetchone()

        if existing_goal:
            db.execute(
                """
                UPDATE budget_goals
                SET goal_cents = ?,
                    start_date = ?,
                    end_date = ?,
                    updated_at = datetime('now')
                WHERE id = ?
                """,
                (goal_cents, start_date, end_date, existing_goal["id"]),
            )
            flash("Budget goal updated.")
        else:
            db.execute(
                """
                INSERT INTO budget_goals
                    (user_id, semester_id, category_id, duration, goal_cents, start_date, end_date, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (uid, sid, cid, duration, goal_cents, start_date, end_date),
            )
            flash("Budget goal created.")

        db.commit()
        return redirect(url_for("categories.categories"))

    categories = db.execute(
        """
        SELECT id, name
        FROM categories
        WHERE user_id = ?
        ORDER BY
          CASE name
            WHEN 'Food' THEN 1
            WHEN 'Health' THEN 2
            WHEN 'Housing' THEN 3
            WHEN 'Other' THEN 4
            WHEN 'Personal' THEN 5
            WHEN 'School Supplies' THEN 6
            WHEN 'Textbooks' THEN 7
            WHEN 'Transportation' THEN 8
            ELSE 99
          END,
          name ASC
        """,
        (uid,),
    ).fetchall()

    goals_raw = db.execute(
        """
        SELECT
            bg.id,
            bg.duration,
            bg.goal_cents,
            bg.start_date,
            bg.end_date,
            c.name AS category_name,
            c.id AS category_id,
            COALESCE(SUM(t.amount_cents), 0) AS spent_cents
        FROM budget_goals bg
        JOIN categories c
          ON c.id = bg.category_id
        LEFT JOIN transactions t
          ON t.user_id = bg.user_id
         AND t.semester_id = bg.semester_id
         AND t.category_id = bg.category_id
         AND t.type = 'expense'
         AND date(t.date) >= date(bg.start_date)
         AND date(t.date) <= date(bg.end_date)
        WHERE bg.user_id = ?
          AND bg.semester_id = ?
          AND bg.is_active = 1
        GROUP BY
            bg.id,
            bg.duration,
            bg.goal_cents,
            bg.start_date,
            bg.end_date,
            c.name,
            c.id
        ORDER BY bg.created_at DESC, bg.id DESC
        """,
        (uid, sid or -1),
    ).fetchall()

    goals = []
    for g in goals_raw:
        goal_cents = g["goal_cents"] or 0
        spent_cents = g["spent_cents"] or 0
        remaining_cents = max(goal_cents - spent_cents, 0)
        over_cents = max(spent_cents - goal_cents, 0)

        percent = 0
        if goal_cents > 0:
            percent = round((spent_cents / goal_cents) * 100)

        if percent >= 100:
            status = "WARNING"
            status_class = "red"
        elif percent >= 75:
            status = "IN PROGRESS"
            status_class = "blue"
        else:
            status = "ACTIVE"
            status_class = "green"

        

        category_name = (g["category_name"] or "").strip().lower()

        icon_file = {
            "food": "foodicon.png",
            "health": "healthicon.png",
            "housing": "housingicon.png",
            "other": "othericon.png",
            "personal": "personalicon.png",
            "school supplies": "suppliesicon.png",
            "textbooks": "booksicon.png",
            "transportation": "transportationicon.png",
        }.get(category_name, "othericon.png")

        subtitle_map = {
            "weekly": "Weekly spending goal",
            "monthly": "Monthly spending goal",
            "semester": "Semester spending goal",
        }

        goals.append(
            {
                "id": g["id"],
                "category_name": g["category_name"],
                "duration": g["duration"].title(),
                "goal_cents": goal_cents,
                "spent_cents": spent_cents,
                "remaining_cents": remaining_cents,
                "over_cents": over_cents,
                "percent": min(percent, 100),
                "status": status,
                "status_class": status_class,
                "start_date": g["start_date"],
                "end_date": g["end_date"],
                "icon_file": icon_file,
                "subtitle": subtitle_map.get(g["duration"], "Spending goal"),
            }
        )

    return render_template(
        "categories.html",
        categories=categories,
        goals=goals,
        semester=semester,
        active_semester_id=sid,
    )