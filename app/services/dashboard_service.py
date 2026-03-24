from datetime import date
from app.common.money import cents_to_money
from app.pacing import compute_pace, safe_to_spend, runout_week_projection


def load_dashboard_data(db, user_id: int, semester_id: int, semester_row):
    aid_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM aid_awards WHERE semester_id = ?",
        (semester_id,),
    ).fetchone()["s"]
    income_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM transactions WHERE semester_id = ? AND user_id = ? AND type='income'",
        (semester_id, user_id),
    ).fetchone()["s"]
    expense_total_cents = db.execute(
        "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM transactions WHERE semester_id = ? AND user_id = ? AND type='expense'",
        (semester_id, user_id),
    ).fetchone()["s"]

    total_funds_cents = int(aid_total_cents) + int(income_total_cents)
    spent_cents = int(expense_total_cents)

    total_funds = cents_to_money(total_funds_cents)
    spent = cents_to_money(spent_cents)
    remaining = max(0.0, total_funds - spent)

    pace = compute_pace(
        start_iso=semester_row["start_date"],
        end_iso=semester_row["end_date"],
        weeks_total=int(semester_row["weeks"]),
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

    category_rows = db.execute(
        """SELECT c.name AS category, COALESCE(SUM(t.amount_cents),0) AS total_cents
             FROM categories c
             LEFT JOIN transactions t
               ON t.category_id = c.id AND t.type='expense' AND t.semester_id=? AND t.user_id=?
             WHERE c.user_id=?
             GROUP BY c.id
             HAVING total_cents > 0
             ORDER BY total_cents DESC""",
        (semester_id, user_id, user_id),
    ).fetchall()

    projection_week = runout_week_projection(
        remaining=remaining,
        spent_so_far=spent,
        week_now=pace.week_now,
    )

    recent = db.execute(
        """SELECT t.*, COALESCE(c.name,'') AS category_name
             FROM transactions t
             LEFT JOIN categories c ON c.id = t.category_id
             WHERE t.user_id=? AND t.semester_id=?
             ORDER BY t.date DESC, t.id DESC
             LIMIT 10""",
        (user_id, semester_id),
    ).fetchall()

    aid_list = db.execute(
        "SELECT * FROM aid_awards WHERE semester_id=? ORDER BY disbursement_date DESC, id DESC",
        (semester_id,),
    ).fetchall()

    return {
        "pace": pace,
        "total_funds": total_funds,
        "spent": spent,
        "remaining": remaining,
        "safe_weekly": safe_weekly,
        "alerts": alerts,
        "categories": category_rows,
        "projection_week": projection_week,
        "recent": recent,
        "aid_list": aid_list,
    }
