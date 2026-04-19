from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.money import money_to_cents
from app.common.session_utils import current_user_id
from app.db import get_db
from app.services.category_service import ensure_default_categories

bp = Blueprint("categories", __name__)


@bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    db = get_db()
    uid = current_user_id()
    ensure_default_categories(db, uid)

    if request.method == "POST":
        category_id = request.form.get("category_id")
        budget_amount = request.form.get("budget_amount") or ""

        if not category_id:
            flash("Please choose a category.")
            return redirect(url_for("categories.categories"))

        budget_cents = money_to_cents(budget_amount)
        if budget_cents is None or budget_cents < 0:
            flash("Enter a valid budget amount.")
            return redirect(url_for("categories.categories"))

        try:
            cid = int(category_id)
        except Exception:
            flash("Invalid category.")
            return redirect(url_for("categories.categories"))

        category = db.execute(
            "SELECT id FROM categories WHERE id = ? AND user_id = ?",
            (cid, uid)
        ).fetchone()

        if not category:
            flash("Category not found.")
            return redirect(url_for("categories.categories"))

        db.execute(
            """
            INSERT INTO category_budgets (user_id, category_id, budget_cents)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, category_id)
            DO UPDATE SET budget_cents = excluded.budget_cents
            """,
            (uid, cid, budget_cents),
        )
        db.commit()
        flash("Budget saved.")
        return redirect(url_for("categories.categories"))

    categories_with_budgets = db.execute(
        """
        SELECT
            c.id,
            c.name,
            COALESCE(cb.budget_cents, 0) AS budget_cents
        FROM categories c
        LEFT JOIN category_budgets cb
            ON cb.category_id = c.id
           AND cb.user_id = c.user_id
        WHERE c.user_id = ?
        ORDER BY c.name ASC
        """,
        (uid,),
    ).fetchall()

    return render_template("categories.html", categories=categories_with_budgets)