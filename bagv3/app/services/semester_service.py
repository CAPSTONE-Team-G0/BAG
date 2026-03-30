from datetime import date


def validate_semester_dates(start_date: str, end_date: str):
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except Exception:
        return None, None, "Invalid date format."

    if end <= start:
        return start, end, "End date must be after start date."

    return start, end, None


def normalize_weeks(value: str, default_weeks: int) -> tuple[int, str | None]:
    try:
        weeks = int(value)
    except Exception:
        weeks = default_weeks

    if weeks < 8 or weeks > 26:
        return weeks, "Weeks must be between 8 and 26."

    return weeks, None
