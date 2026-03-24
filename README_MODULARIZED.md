# Bag (Flask) — Modularized Team Version

## What changed
The original `app/core.py` was split into feature-based route files and shared services so multiple people can work without constantly editing the same file.

## New structure
- `app/auth.py` → login/register/logout only
- `app/routes/home.py` → `/`
- `app/routes/profile.py` → profile page
- `app/routes/semesters.py` → semester list/create/select
- `app/routes/aid.py` → aid form
- `app/routes/transactions.py` → income/expense form
- `app/routes/categories.py` → category management
- `app/routes/dashboard.py` → dashboard page
- `app/services/category_service.py` → default category seeding
- `app/services/semester_service.py` → semester validation helpers
- `app/services/dashboard_service.py` → dashboard calculations/data loading
- `app/common/money.py` → cents conversion helpers
- `app/common/session_utils.py` → active user/semester session helpers
- `app/common/constants.py` → shared constants

## Suggested team ownership
- Person 1: `auth.py` + templates for login/register
- Person 2: `routes/profile.py` and `routes/semesters.py`
- Person 3: `routes/aid.py`, `routes/transactions.py`, `routes/categories.py`
- Person 4: `routes/dashboard.py` + `services/dashboard_service.py` + dashboard template/CSS
- Person 5: `db.py`, `schema.sql`, tests, README, integration cleanup

## Team rules to avoid breakage
1. Do not put new route logic back into one giant file.
2. Put shared math/validation in `services/` or `common/`.
3. Keep each blueprint responsible for one feature.
4. If two features need the same helper, move it out of the route file.
5. Agree on one person to handle merges and run the app before pushing.

## High-risk files
These should be edited carefully because changes affect everyone:
- `app/__init__.py`
- `app/db.py`
- `app/schema.sql`
- shared helpers in `app/common/`
- shared services in `app/services/`
