from . import __name__
from app.common.constants import DEFAULT_CATEGORIES


def ensure_default_categories(db, user_id: int) -> None:
    for name in DEFAULT_CATEGORIES:
        db.execute(
            "INSERT OR IGNORE INTO categories (user_id, name) VALUES (?, ?)",
            (user_id, name),
        )
    db.commit()
