import os
import sys
import sqlite3
from flask import current_app, g
import click


def _db_path():
    """
    In normal VS Code/dev mode, use Flask's instance folder.
    In the packaged .exe, create/use an instance folder next to the .exe.
    """
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
        instance = os.path.join(base_dir, "instance")
    else:
        instance = current_app.instance_path

    os.makedirs(instance, exist_ok=True)
    return os.path.join(instance, current_app.config["DATABASE"])


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(_db_path(), detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    db.commit()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

    with app.app_context():
        db_path = _db_path()

        if not os.path.exists(db_path):
            init_db()