from app import create_app
from app.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db = get_db()

    users = [
        ("student1@bag.com", "password123", "student"),
        ("student2@bag.com", "password123", "student"),
        ("parent@bag.com", "password123", "parent"),
    ]

    for email, password, role in users:
        existing = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        if not existing:
            db.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, generate_password_hash(password), role),
            )

    db.commit()

    student1 = db.execute(
        "SELECT id FROM users WHERE email = ?",
        ("student1@bag.com",),
    ).fetchone()["id"]

    student2 = db.execute(
        "SELECT id FROM users WHERE email = ?",
        ("student2@bag.com",),
    ).fetchone()["id"]

    demo_students = [
        (student1, "Student One", 6200),
        (student2, "Student Two", 5400),
    ]

    categories = [
        "Housing",
        "Food",
        "Transportation",
        "Textbooks",
        "Personal",
        "Health",
        "School Supplies",
        "Other",
    ]

    semester_data = [
        ("Fall 2025", "2025-08-19", "2025-12-08", 16),
        ("Spring 2026", "2026-01-14", "2026-05-13", 16),
        ("Summer 2026", "2026-05-26", "2026-07-23", 8),
    ]

    for uid, display_name, aid_amount_dollars in demo_students:
        existing_profile = db.execute(
            "SELECT user_id FROM profiles WHERE user_id = ?",
            (uid,),
        ).fetchone()

        if not existing_profile:
            db.execute(
                """
                INSERT INTO profiles
                    (user_id, display_name, default_semester_weeks, profile_image)
                VALUES (?, ?, ?, ?)
                """,
                (uid, display_name, 16, "baglogopurple.png"),
            )

        for cat in categories:
            db.execute(
                "INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)",
                (uid, cat),
            )

        for sem_name, start_date, end_date, weeks in semester_data:
            existing_semester = db.execute(
                """
                SELECT id FROM semesters
                WHERE user_id = ?
                  AND name = ?
                """,
                (uid, sem_name),
            ).fetchone()

            if not existing_semester:
                db.execute(
                    """
                    INSERT INTO semesters
                        (user_id, name, start_date, end_date, weeks)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (uid, sem_name, start_date, end_date, weeks),
                )

    db.commit()

    demo_expenses = {
        student1: [
            ("Housing", 95000, "2026-01-20", "January rent"),
            ("Food", 12850, "2026-01-22", "Groceries"),
            ("Transportation", 4200, "2026-01-25", "Gas"),
            ("Textbooks", 18500, "2026-01-28", "Course books"),
            ("Food", 1675, "2026-02-02", "Lunch on campus"),
            ("Personal", 3900, "2026-02-05", "Laundry and supplies"),
            ("Health", 2500, "2026-02-10", "Pharmacy"),
            ("Food", 7420, "2026-02-14", "Groceries"),
            ("Transportation", 5200, "2026-02-18", "Gas"),
            ("School Supplies", 3150, "2026-02-20", "Notebook and pens"),
        ],
        student2: [
            ("Housing", 80000, "2026-01-18", "Rent"),
            ("Food", 9200, "2026-01-23", "Groceries"),
            ("Transportation", 3600, "2026-01-24", "Gas"),
            ("Textbooks", 12200, "2026-01-29", "Books"),
            ("Personal", 4500, "2026-02-04", "Clothing"),
            ("Food", 6800, "2026-02-08", "Groceries"),
            ("Health", 1800, "2026-02-12", "Medicine"),
            ("Transportation", 4100, "2026-02-17", "Gas"),
        ],
    }

    for uid, display_name, aid_amount_dollars in demo_students:
        spring = db.execute(
            """
            SELECT id FROM semesters
            WHERE user_id = ?
              AND name = ?
            """,
            (uid, "Spring 2026"),
        ).fetchone()

        spring_id = spring["id"]

        existing_aid = db.execute(
            """
            SELECT id FROM aid_awards
            WHERE semester_id = ?
              AND label = ?
            """,
            (spring_id, "Spring financial aid refund"),
        ).fetchone()

        if not existing_aid:
            db.execute(
                """
                INSERT INTO aid_awards
                    (semester_id, source_type, label, amount_cents, disbursement_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    spring_id,
                    "FAFSA",
                    "Spring financial aid refund",
                    aid_amount_dollars * 100,
                    "2026-01-15",
                ),
            )

        for cat_name, amount_cents, tx_date, note in demo_expenses[uid]:
            cat = db.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ?",
                (uid, cat_name),
            ).fetchone()

            existing_tx = db.execute(
                """
                SELECT id FROM transactions
                WHERE user_id = ?
                  AND semester_id = ?
                  AND amount_cents = ?
                  AND date = ?
                  AND note = ?
                """,
                (uid, spring_id, amount_cents, tx_date, note),
            ).fetchone()

            if not existing_tx:
                db.execute(
                    """
                    INSERT INTO transactions
                        (user_id, semester_id, type, amount_cents, date, category_id, note)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (uid, spring_id, "expense", amount_cents, tx_date, cat["id"], note),
                )

        goals = [
            ("Housing", "semester", 420000),
            ("Food", "monthly", 45000),
            ("Transportation", "monthly", 22000),
            ("Textbooks", "semester", 30000),
            ("Personal", "monthly", 18000),
        ]

        for cat_name, duration, goal_cents in goals:
            cat = db.execute(
                "SELECT id FROM categories WHERE user_id = ? AND name = ?",
                (uid, cat_name),
            ).fetchone()

            existing_goal = db.execute(
                """
                SELECT id FROM budget_goals
                WHERE user_id = ?
                  AND semester_id = ?
                  AND category_id = ?
                  AND duration = ?
                  AND is_active = 1
                """,
                (uid, spring_id, cat["id"], duration),
            ).fetchone()

            if not existing_goal:
                db.execute(
                    """
                    INSERT INTO budget_goals
                        (user_id, semester_id, category_id, duration, goal_cents, start_date, end_date, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (
                        uid,
                        spring_id,
                        cat["id"],
                        duration,
                        goal_cents,
                        "2026-01-14",
                        "2026-05-13",
                    ),
                )

    db.commit()

    print("✅ Full demo data created successfully!")
    print("Student 1: student1@bag.com / password123")
    print("Student 2: student2@bag.com / password123")
    print("Parent: parent@bag.com / password123")