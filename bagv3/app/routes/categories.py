from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
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
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Category name is required.")
        else:
            db.execute("INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)", (uid, name))
            db.commit()
            flash("Category saved.")
        return redirect(url_for("categories.categories"))

    cats = db.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC", (uid,)).fetchall()
    return render_template("categories.html", categories=cats)
