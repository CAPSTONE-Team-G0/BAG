from datetime import date
from flask import Blueprint, flash, redirect, render_template, request, url_for
from app.auth import login_required
from app.common.money import money_to_cents
from app.common.session_utils import active_semester_id, current_user_id
from app.db import get_db

bp = Blueprint("aid", __name__)


@bp.route("/aid/new", methods=["GET", "POST"])
@login_required
def aid_new():
    db = get_db()
    uid = current_user_id()
    sid = active_semester_id()

    if sid is None:
        flash("Create and select a semester first.")
        return redirect(url_for("semesters.semester_new"))

    if request.method == "POST":
        source_type = (request.form.get("source_type") or "FAFSA").strip()
        label = (request.form.get("label") or "").strip() or source_type
        amount = money_to_cents(request.form.get("amount") or "")
        disb = (request.form.get("disbursement_date") or "").strip()

        if amount is None or amount == 0:
            flash("Amount must be greater than 0.")
            return render_template("aid_new.html")

        if not disb:
            flash("Disbursement date is required.")
            return render_template("aid_new.html")

        try:
            date.fromisoformat(disb)
        except Exception:
            flash("Invalid disbursement date.")
            return render_template("aid_new.html")

        sem = db.execute(
            "SELECT id FROM semesters WHERE id = ? AND user_id = ?",
            (sid, uid),
        ).fetchone()

        if not sem:
            flash("Invalid active semester.")
            return redirect(url_for("semesters.semesters"))

        db.execute(
            """
            INSERT INTO aid_awards
            (semester_id, source_type, label, amount_cents, disbursement_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (sid, source_type, label, amount, disb),
        )
        db.commit()

        flash("Funds saved.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("aid_new.html")


@bp.route("/aid/edit/<int:aid_id>", methods=["GET", "POST"])
@login_required
def aid_edit(aid_id):
    db = get_db()
    uid = current_user_id()

    aid = db.execute(
        """
        SELECT aa.*
        FROM aid_awards aa
        JOIN semesters s ON s.id = aa.semester_id
        WHERE aa.id = ?
          AND s.user_id = ?
        """,
        (aid_id, uid),
    ).fetchone()

    if aid is None:
        flash("Funding entry not found.")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        source_type = (request.form.get("source_type") or "").strip()
        label = (request.form.get("label") or "").strip() or source_type
        amount = money_to_cents(request.form.get("amount") or "")
        disb = (request.form.get("disbursement_date") or "").strip()

        if amount is None or amount == 0:
            flash("Amount must be greater than 0.")
            return render_template("aid_edit.html", aid=aid)

        if not disb:
            flash("Disbursement date is required.")
            return render_template("aid_edit.html", aid=aid)

        try:
            date.fromisoformat(disb)
        except Exception:
            flash("Invalid disbursement date.")
            return render_template("aid_edit.html", aid=aid)

        db.execute(
            """
            UPDATE aid_awards
            SET source_type = ?,
                label = ?,
                amount_cents = ?,
                disbursement_date = ?
            WHERE id = ?
            """,
            (source_type, label, amount, disb, aid_id),
        )
        db.commit()

        flash("Funding entry updated.")
        return redirect(url_for("dashboard.dashboard"))

    return render_template("aid_edit.html", aid=aid)


@bp.route("/aid/delete/<int:aid_id>", methods=["POST"])
@login_required
def aid_delete(aid_id):
    db = get_db()
    uid = current_user_id()

    db.execute(
        """
        DELETE FROM aid_awards
        WHERE id = ?
          AND semester_id IN (
            SELECT id FROM semesters WHERE user_id = ?
          )
        """,
        (aid_id, uid),
    )
    db.commit()

    flash("Funding entry deleted.")
    return redirect(url_for("dashboard.dashboard"))