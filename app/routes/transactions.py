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
    cats = db.execute(
        "SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC",
        (uid,)
    ).fetchall()

    if request.method == "POST":
        ttype = "expense"
        amount = money_to_cents(request.form.get("amount") or "")
        tdate = (request.form.get("date") or "").strip()
        category_id = request.form.get("category_id") or None
        note = (request.form.get("note") or "").strip()

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

        if not category_id:
            flash("Please select a category.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())

        cat_id = None

        try:
            cid = int(category_id)
            ok = db.execute(
                "SELECT id, name FROM categories WHERE id = ? AND user_id = ?",
                (cid, uid)
            ).fetchone()

            if ok:
                cat_id = cid

                if ok["name"].lower() == "other" and not note:
                    flash("Please add a note when selecting 'Other'.")
                    return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())

        except Exception:
            cat_id = None

        if cat_id is None:
            flash("Please select a valid category.")
            return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())

        db.execute(
            """
            INSERT INTO transactions
            (user_id, semester_id, type, amount_cents, date, category_id, note)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (uid, sid, ttype, amount, tdate, cat_id, note),
        )

        db.commit()
        flash("Expense saved.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template(
        "transaction_new.html",
        categories=cats,
        today=date.today().isoformat()
    )


@bp.route("/transaction/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def transaction_edit(transaction_id):
    db = get_db()
    uid = current_user_id()

    transaction = db.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, uid)
    ).fetchone()

    if not transaction:
        flash("Transaction not found.")
        return redirect(url_for("dashboard.dashboard"))

    categories = db.execute(
        "SELECT * FROM categories WHERE user_id = ? ORDER BY name",
        (uid,)
    ).fetchall()

    if request.method == "POST":
        category_id = request.form.get("category_id")
        note = (request.form.get("note") or "").strip()
        amount = money_to_cents(request.form.get("amount"))
        tdate = request.form.get("date")

        if amount is None or amount == 0:
            flash("Amount must be greater than 0.")
            return render_template("transaction_edit.html", transaction=transaction, categories=categories)

        if not category_id:
            flash("Please select a category.")
            return render_template("transaction_edit.html", transaction=transaction, categories=categories)

        cat_name = db.execute(
            "SELECT name FROM categories WHERE id = ? AND user_id = ?",
            (category_id, uid)
        ).fetchone()

        if cat_name and cat_name["name"].lower() == "other" and not note:
            flash("Please add a note when selecting 'Other'.")
            return render_template("transaction_edit.html", transaction=transaction, categories=categories)

        db.execute(
            """
            UPDATE transactions
            SET type=?, amount_cents=?, date=?, category_id=?, note=?
            WHERE id=? AND user_id=?
            """,
            (
                "expense",
                amount,
                tdate,
                category_id,
                note,
                transaction_id,
                uid
            )
        )

        db.commit()
        flash("Expense updated.")
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
    uid = current_user_id()

    db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, uid)
    )

    db.commit()
    flash("Transaction deleted.")
    return redirect(url_for("dashboard.dashboard"))