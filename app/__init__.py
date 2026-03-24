from flask import Flask
from .db import init_app as init_db_app
from .auth import bp as auth_bp
from .routes.home import bp as home_bp
from .routes.profile import bp as profile_bp
from .routes.semesters import bp as semesters_bp
from .routes.aid import bp as aid_bp
from .routes.transactions import bp as transactions_bp
from .routes.categories import bp as categories_bp
from .routes.dashboard import bp as dashboard_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev-change-me",
        DATABASE="bag.sqlite3",
    )

    init_db_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(semesters_bp)
    app.register_blueprint(aid_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(dashboard_bp)

    return app
