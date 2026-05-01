from __future__ import annotations
from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .db import get_db
from .auth import login_required
from .pacing import compute_pace, safe_to_spend, runout_week_projection

bp = Blueprint("core", __name__, url_prefix="")

DEFAULT_CATEGORIES = [
    "Housing", "Food", "Transportation", "Textbooks",
    "Personal", "Health", "School Supplies", "Other"
]

US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

PROFILE_IMAGE_CHOICES = [
    "baglogo.png",
    "baglogogreen.png",
    "baglogored.png",
    "baglogopurple.png",
]


def _user_id() -> int:
    return int(session["user_id"])


def _active_semester_id() -> int | None:
    sid = session.get("active_semester_id")
    return int(sid) if sid is not None else None


def _ensure_default_categories(db, user_id: int):
    for name in DEFAULT_CATEGORIES:
        db.execute(
            "INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
    db.commit()


def _money_to_cents(s: str) -> int | None:
    try:
        v = float(s)
    except Exception:
        return None
    if v < 0:
        return None
    return int(round(v * 100))


def _cents_to_money(cents: int) -> float:
    return (cents or 0) / 100.0


@bp.route("/")
def home():
    if session.get("user_id") is None:
        return redirect(url_for("auth.login"))
    return redirect(url_for("core.dashboard"))




@bp.route("/semesters")
@login_required
def semesters():
    db = get_db()
    uid = _user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    sems = db.execute(
        "SELECT * FROM semesters WHERE user_id = ?",
        (uid,),
    ).fetchall()

    today = date.today().isoformat()

    semesters_with_status = []
    for sem in sems:
        sem_dict = dict(sem)
        sem_dict["is_active"] = sem_dict["start_date"] <= today <= sem_dict["end_date"]
        semesters_with_status.append(sem_dict)

    return render_template(
        "semesters.html",
        semesters=semesters_with_status,
        profile=prof,
        today=today,
    )


@bp.route("/semester/new", methods=["GET", "POST"])
@login_required
def semester_new():
    db = get_db()
    uid = _user_id()
    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()
    default_weeks = int(prof["default_semester_weeks"]) if prof else 16

    if request.method == "POST":
        name = (request.form.get("name") or "").strip() or "My Semester"
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()
        weeks = request.form.get("weeks") or str(default_weeks)

        if not start_date or not end_date:
            flash("Start date and end date are required.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        try:
            sd = date.fromisoformat(start_date)
            ed = date.fromisoformat(end_date)
        except Exception:
            flash("Invalid date format.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        if ed <= sd:
            flash("End date must be after start date.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        try:
            weeks_i = int(weeks)
        except Exception:
            weeks_i = default_weeks

        if weeks_i < 8 or weeks_i > 26:
            flash("Weeks must be between 8 and 26.")
            return render_template("semester_new.html", default_weeks=default_weeks)

        db.execute(
            "INSERT INTO semesters (user_id, name, start_date, end_date, weeks) VALUES (?, ?, ?, ?, ?)",
            (uid, name, start_date, end_date, weeks_i),
        )
        db.commit()

        new_id = db.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
        session["active_semester_id"] = int(new_id)

        flash("Semester created and selected.")
        return redirect(url_for("core.dashboard"))

    return render_template("semester_new.html", default_weeks=default_weeks)


@bp.route("/semester/select/<int:semester_id>")
@login_required
def semester_select(semester_id: int):
    db = get_db()
    uid = _user_id()
    row = db.execute(
        "SELECT id FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid),
    ).fetchone()

    if not row:
        flash("Semester not found.")
        return redirect(url_for("core.semesters"))

    session["active_semester_id"] = semester_id
    flash("Semester selected.")
    return redirect(url_for("core.dashboard"))

@bp.route("/semester/edit/<int:semester_id>", methods=["GET", "POST"])
@login_required
def semester_edit(semester_id: int):
    db = get_db()
    uid = _user_id()

    sem = db.execute(
        "SELECT * FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid),
    ).fetchone()

    if not sem:
        flash("Semester not found.")
        return redirect(url_for("core.semesters"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip() or "My Semester"
        start_date = (request.form.get("start_date") or "").strip()
        end_date = (request.form.get("end_date") or "").strip()
        weeks = request.form.get("weeks") or "16"

        if not start_date or not end_date:
            flash("Start date and end date are required.")
            return render_template("semester_edit.html", semester=sem)

        try:
            sd = date.fromisoformat(start_date)
            ed = date.fromisoformat(end_date)
        except Exception:
            flash("Invalid date format.")
            return render_template("semester_edit.html", semester=sem)

        if ed <= sd:
            flash("End date must be after start date.")
            return render_template("semester_edit.html", semester=sem)

        try:
            weeks_i = int(weeks)
        except Exception:
            weeks_i = 16

        if weeks_i < 8 or weeks_i > 26:
            flash("Weeks must be between 8 and 26.")
            return render_template("semester_edit.html", semester=sem)

        db.execute(
            """
            UPDATE semesters
            SET name = ?, start_date = ?, end_date = ?, weeks = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, start_date, end_date, weeks_i, semester_id, uid),
        )
        db.commit()

        flash("Semester updated.")
        return redirect(url_for("core.semesters"))

    return render_template("semester_edit.html", semester=sem)


@bp.route("/semester/delete/<int:semester_id>", methods=["POST"])
@login_required
def semester_delete(semester_id: int):
    db = get_db()
    uid = _user_id()

    db.execute(
        "DELETE FROM semesters WHERE id = ? AND user_id = ?",
        (semester_id, uid),
    )
    db.commit()

    active_id = session.get("active_semester_id")
    if active_id is not None and int(active_id) == semester_id:
        session.pop("active_semester_id", None)

    flash("Semester deleted.")
    return redirect(url_for("core.semesters"))


@bp.route("/aid/new", methods=["GET", "POST"])
@login_required
def aid_new():
    db = get_db()
    uid = _user_id()
    sid = _active_semester_id()

    if sid is None:
        flash("Create and select a semester first.")
        return redirect(url_for("core.semester_new"))

    if request.method == "POST":
        source_type = (request.form.get("source_type") or "FAFSA").strip()
        label = (request.form.get("label") or "").strip()
        amount = _money_to_cents(request.form.get("amount") or "")
        disb = (request.form.get("disbursement_date") or "").strip()

        if source_type == "Other" and not label:
            flash("Please enter a label when selecting 'Other'.")
            return render_template("aid_new.html")

        if not label:
            label = source_type

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
            return redirect(url_for("core.semesters"))

        db.execute(
            "INSERT INTO aid_awards (semester_id, source_type, label, amount_cents, disbursement_date) VALUES (?, ?, ?, ?, ?)",
            (sid, source_type, label, amount, disb),
        )
        db.commit()

        flash("Aid saved.")
        return redirect(url_for("core.dashboard"))

    return render_template("aid_new.html")
@bp.route("/aid/edit/<int:aid_id>", methods=["GET", "POST"])
@login_required
def aid_edit(aid_id: int):
    db = get_db()
    uid = _user_id()

    aid = db.execute(
        """
        SELECT a.*
        FROM aid_awards a
        JOIN semesters s ON s.id = a.semester_id
        WHERE a.id = ? AND s.user_id = ?
        """,
        (aid_id, uid),
    ).fetchone()

    if not aid:
        flash("Funding entry not found.")
        return redirect(url_for("core.dashboard"))

    if request.method == "POST":
        source_type = (request.form.get("source_type") or "FAFSA").strip()
        label = (request.form.get("label") or "").strip()
        amount = _money_to_cents(request.form.get("amount") or "")
        disb = (request.form.get("disbursement_date") or "").strip()

        if source_type == "Other" and not label:
            flash("Please enter a label when selecting 'Other'.")
            return render_template("aid_edit.html", aid=aid)

        if not label:
            label = source_type

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
            SET source_type = ?, label = ?, amount_cents = ?, disbursement_date = ?
            WHERE id = ?
            """,
            (source_type, label, amount, disb, aid_id),
        )
        db.commit()

        flash("Funding updated.")
        return redirect(url_for("core.dashboard"))

    return render_template("aid_edit.html", aid=aid)


@bp.route("/aid/delete/<int:aid_id>", methods=["POST"])
@login_required
def aid_delete(aid_id: int):
    db = get_db()
    uid = _user_id()

    db.execute(
        """
        DELETE FROM aid_awards
        WHERE id = ?
          AND semester_id IN (SELECT id FROM semesters WHERE user_id = ?)
        """,
        (aid_id, uid),
    )
    db.commit()

    flash("Funding deleted.")
    return redirect(url_for("core.dashboard"))


@bp.route("/transaction/new", methods=["GET", "POST"])
@login_required
def transaction_new():
    db = get_db()
    uid = _user_id()
    sid = _active_semester_id()

    if sid is None:
        flash("Create and select a semester first.")
        return redirect(url_for("core.semester_new"))

    _ensure_default_categories(db, uid)
    cats = db.execute(
        "SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC",
        (uid,),
    ).fetchall()

    if request.method == "POST":
        ttype = (request.form.get("type") or "expense").strip()
        amount = _money_to_cents(request.form.get("amount") or "")
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
                    (cid, uid),
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
        return redirect(url_for("core.dashboard"))

    return render_template("transaction_new.html", categories=cats, today=date.today().isoformat())


@bp.route("/transaction/edit/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def transaction_edit(transaction_id: int):
    db = get_db()
    uid = _user_id()

    _ensure_default_categories(db, uid)
    cats = db.execute(
        "SELECT * FROM categories WHERE user_id = ? ORDER BY name ASC",
        (uid,),
    ).fetchall()

    tx = db.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, uid),
    ).fetchone()

    if not tx:
        flash("Transaction not found.")
        return redirect(url_for("core.dashboard"))

    if request.method == "POST":
        ttype = (request.form.get("type") or "expense").strip()
        amount = _money_to_cents(request.form.get("amount") or "")
        tdate = (request.form.get("date") or "").strip()
        category_id = request.form.get("category_id") or None
        note = (request.form.get("note") or "").strip()

        if ttype not in ("income", "expense"):
            flash("Invalid transaction type.")
            return render_template("transaction_edit.html", transaction=tx, categories=cats)

        if amount is None or amount == 0:
            flash("Amount must be greater than 0.")
            return render_template("transaction_edit.html", transaction=tx, categories=cats)

        if not tdate:
            flash("Date is required.")
            return render_template("transaction_edit.html", transaction=tx, categories=cats)

        try:
            date.fromisoformat(tdate)
        except Exception:
            flash("Invalid date.")
            return render_template("transaction_edit.html", transaction=tx, categories=cats)

        cat_id = None
        if category_id:
            try:
                cid = int(category_id)
                ok = db.execute(
                    "SELECT id FROM categories WHERE id = ? AND user_id = ?",
                    (cid, uid),
                ).fetchone()
                if ok:
                    cat_id = cid
            except Exception:
                cat_id = None

        db.execute(
            """
            UPDATE transactions
            SET type = ?, amount_cents = ?, date = ?, category_id = ?, note = ?
            WHERE id = ? AND user_id = ?
            """,
            (ttype, amount, tdate, cat_id, note, transaction_id, uid),
        )
        db.commit()

        flash("Transaction updated.")
        return redirect(url_for("core.dashboard"))

    return render_template("transaction_edit.html", transaction=tx, categories=cats)


@bp.route("/transaction/delete/<int:transaction_id>", methods=["POST"])
@login_required
def transaction_delete(transaction_id: int):
    db = get_db()
    uid = _user_id()

    db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, uid),
    )
    db.commit()

    flash("Transaction deleted.")
    return redirect(url_for("core.dashboard"))


@bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    db = get_db()
    uid = _user_id()
    sid = _active_semester_id()
    _ensure_default_categories(db, uid)

    semester = None
    if sid is not None:
        semester = db.execute(
            "SELECT * FROM semesters WHERE id = ? AND user_id = ?",
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

    def _goal_date_range(duration: str):
        today = date.today()
        if duration == "weekly":
            return today.isoformat(), (today + timedelta(days=6)).isoformat()
        if duration == "monthly":
            return today.isoformat(), (today + timedelta(days=29)).isoformat()
        if duration == "semester":
            if semester:
                return semester["start_date"], semester["end_date"]
            return today.isoformat(), (today + timedelta(days=111)).isoformat()
        return None, None

    if request.method == "POST":
        category_id = request.form.get("category_id")
        goal_amount = (request.form.get("goal_amount") or "").strip()
        duration = (request.form.get("duration") or "").strip().lower()

        if not sid:
            flash("Please create or select a semester first.")
            return redirect(url_for("core.semesters"))

        if not category_id:
            flash("Please choose a category.")
            return redirect(url_for("core.categories"))

        if duration not in {"weekly", "monthly", "semester"}:
            flash("Please choose a valid duration.")
            return redirect(url_for("core.categories"))

        goal_cents = _money_to_cents(goal_amount)
        if goal_cents is None or goal_cents <= 0:
            flash("Enter a valid goal amount.")
            return redirect(url_for("core.categories"))

        try:
            cid = int(category_id)
        except Exception:
            flash("Invalid category.")
            return redirect(url_for("core.categories"))

        category = db.execute(
            "SELECT id, name FROM categories WHERE id = ? AND user_id = ?",
            (cid, uid),
        ).fetchone()

        if not category:
            flash("Category not found.")
            return redirect(url_for("core.categories"))

        start_date, end_date = _goal_date_range(duration)
        if not start_date or not end_date:
            flash("Could not create that goal.")
            return redirect(url_for("core.categories"))

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
                SET goal_cents = ?, start_date = ?, end_date = ?, updated_at = datetime('now')
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
        return redirect(url_for("core.categories"))

    categories = db.execute(
        "SELECT id, name FROM categories WHERE user_id = ? ORDER BY name ASC",
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
            COALESCE(SUM(t.amount_cents), 0) AS spent_cents
        FROM budget_goals bg
        JOIN categories c ON c.id = bg.category_id
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
        GROUP BY bg.id, bg.duration, bg.goal_cents, bg.start_date, bg.end_date, c.name
        ORDER BY bg.id DESC
        """,
        (uid, sid or -1),
    ).fetchall()

    icon_map = {
        "food": "🍴",
        "food & dining": "🍴",
        "health": "⚕",
        "housing": "⌂",
        "other": "•",
        "personal": "◐",
        "school supplies": "✎",
        "textbooks": "📘",
        "transportation": "🚗",
    }

    goals = []
    for g in goals_raw:
        goal_cents = g["goal_cents"] or 0
        spent_cents = g["spent_cents"] or 0
        remaining_cents = max(goal_cents - spent_cents, 0)
        over_cents = max(spent_cents - goal_cents, 0)
        percent = round((spent_cents / goal_cents) * 100) if goal_cents > 0 else 0

        if percent >= 100:
            status, status_class = "WARNING", "red"
        elif percent >= 75:
            status, status_class = "IN PROGRESS", "blue"
        else:
            status, status_class = "ACTIVE", "green"

        key = (g["category_name"] or "").strip().lower()
        goals.append({
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
            "icon": icon_map.get(key, (g["category_name"] or "?")[0].upper()),
        })

    return render_template("categories.html", categories=categories, goals=goals, semester=semester)


@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    uid = _user_id()
    sid = _active_semester_id()

    prof = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    if sid is None:
        sems = db.execute(
            "SELECT * FROM semesters WHERE user_id = ? ORDER BY start_date DESC, end_date DESC",
            (uid,),
        ).fetchall()
        return render_template("dashboard_empty.html", semesters=sems, profile=prof)

    sem = db.execute(
        "SELECT * FROM semesters WHERE id = ? AND user_id = ?",
        (sid, uid),
    ).fetchone()

    if not sem:
        session.pop("active_semester_id", None)
        flash("Active semester not found. Please select a semester.")
        return redirect(url_for("core.semesters"))

    aid_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM aid_awards WHERE semester_id = ?",
        (sid,),
    ).fetchone()["s"]

    income_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM transactions WHERE semester_id = ? AND user_id = ? AND type='income'",
        (sid, uid),
    ).fetchone()["s"]

    expense_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM transactions WHERE semester_id = ? AND user_id = ? AND type='expense'",
        (sid, uid),
    ).fetchone()["s"]

    total_funds_cents = int(aid_total_cents) + int(income_total_cents)
    spent_cents = int(expense_total_cents)

    total_funds = _cents_to_money(total_funds_cents)
    spent = _cents_to_money(spent_cents)
    remaining = max(0.0, total_funds - spent)

    pace = compute_pace(
        start_iso=sem["start_date"],
        end_iso=sem["end_date"],
        weeks_total=int(sem["weeks"]),
        today=date.today(),
        funds_spent=spent,
        total_funds=total_funds,
    )
    safe_weekly = safe_to_spend(remaining, pace.week_now, pace.weeks_total)

    alerts = []
    if total_funds > 0:
        if pace.funds_spent_pct >= 100:
            alerts.append("You’ve reached 100% of your funds. Time to pause spending and reassess.")
        elif pace.funds_spent_pct >= 90:
            alerts.append("You’ve used 90% of your funds. Consider tightening spending until the semester ends.")
        elif pace.funds_spent_pct >= 75:
            alerts.append("You’ve used 75% of your funds. Keep an eye on your pace this week.")

    cat_rows = db.execute(
        """
        SELECT c.name AS category, COALESCE(SUM(t.amount_cents),0) AS total_cents
        FROM categories c
        LEFT JOIN transactions t
          ON t.category_id = c.id AND t.type='expense' AND t.semester_id=? AND t.user_id=?
        WHERE c.user_id=?
        GROUP BY c.id
        HAVING total_cents > 0
        ORDER BY total_cents DESC
        """,
        (sid, uid, uid),
    ).fetchall()

    proj = runout_week_projection(remaining=remaining, spent_so_far=spent, week_now=pace.week_now)

    recent = db.execute(
        """
        SELECT t.*, COALESCE(c.name,'') AS category_name
        FROM transactions t
        LEFT JOIN categories c ON c.id = t.category_id
        WHERE t.user_id=? AND t.semester_id=?
        ORDER BY t.date DESC, t.id DESC
        LIMIT 10
        """,
        (uid, sid),
    ).fetchall()

    aid_list = db.execute(
        "SELECT * FROM aid_awards WHERE semester_id=? ORDER BY disbursement_date DESC, id DESC",
        (sid,),
    ).fetchall()

    return render_template(
        "dashboard.html",
        profile=prof,
        semester=sem,
        pace=pace,
        total_funds=total_funds,
        spent=spent,
        remaining=remaining,
        safe_weekly=safe_weekly,
        alerts=alerts,
        categories=cat_rows,
        projection_week=proj,
        recent=recent,
        aid_list=aid_list,
    )
