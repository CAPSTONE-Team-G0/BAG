from flask import session


def current_user_id() -> int:
    return int(session["user_id"])


def active_semester_id() -> int | None:
    sid = session.get("active_semester_id")
    return int(sid) if sid is not None else None
