from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.money import money_to_cents
from app.common.session_utils import active_semester_id, current_user_id
from app.db import get_db
from app.services.category_service import ensure_default_categories

bp = Blueprint("transactions", __name__)


@bp.route("/transaction/new", methods=["GET", "POST"])
@login_required
def transaction_new():
    db = get_db()
    uid = current_user_id()
    sid = active_semester_id()
    if sid is None:
        flash("Create and select a semester first.")
        return redirect(url_for("semesters.semester_new"))

    ensure_default_categories(db, uid)
    cats = db.execute("SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC", (uid,)).fetchall()

    if request.method == "POST":
        ttype = (request.form.get("type") or "expense").strip()
        amount = money_to_cents(request.form.get("amount") or "")
        tdate = (request.form.get("date") or "").strip()
        category_id = request.form.get("category_id") or None
        note = (request.form.get("note") or "").strip()

        if ttype not in ("income", "expense"):
            flash("Invalid transaction type.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())
        if amount is None or amount == 0:
            flash("Amount must be greater than 0.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())
        if not tdate:
            flash("Date is required.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())
        try:
            date.fromisoformat(tdate)
        except Exception:
            flash("Invalid date.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())

        cat_id = None
        if category_id:
            try:
                cid = int(category_id)
                ok = db.execute("SELECT id FROM categories WHERE id = ? AND user_id = ?", (cid, uid)).fetchone()
                if ok:
                    cat_id = cid
            except Exception:
                cat_id = None

        db.execute(
            "INSERT INTO transactions (user_id, semester_id, type, amount_cents, date, category_id, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (uid, sid, ttype, amount, tdate, cat_id, note),
        )
        db.commit()
        flash("Transaction saved.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())
