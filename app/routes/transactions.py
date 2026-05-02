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
        new_category = (request.form.get("new_category") or "").strip()
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

        if new_category:
            db.execute(
                "INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)",
                (uid, new_category),
            )
            db.commit()

            created_cat = db.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ?",
                (uid, new_category),
            ).fetchone()

            if created_cat:
                cat_id = created_cat["id"]

        elif category_id:
            try:
                cid = int(category_id)
                ok = db.execute(
                    "SELECT id FROM categories WHERE id = ? AND user_id = ?",
                    (cid, uid)
                ).fetchone()
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

@bp.route("/transaction/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def transaction_edit(transaction_id):
    db = get_db()

    transaction = db.execute(
        "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
    ).fetchone()

    categories = db.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    if request.method == "POST":
        db.execute("""
            UPDATE transactions
            SET type=?, amount_cents=?, date=?, category_id=?, note=?
            WHERE id=?
        """, (
            request.form.get("type"),
            money_to_cents(request.form.get("amount")),
            request.form.get("date"),
            request.form.get("category_id"),
            request.form.get("note"),
            transaction_id
        ))

        db.commit()
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "transaction_edit.html",
        transaction=transaction,
        categories=categories
    )


@bp.route("/transaction/delete/<int:transaction_id>", methods=["POST"])
@login_required
def transaction_delete(transaction_id):
    db = get_db()
    db.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    db.commit()
    return redirect(url_for("dashboard.dashboard"))
