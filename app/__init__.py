from flask import Flask, session
from .db import init_app as init_db_app, get_db
from .core import bp as core_bp
from .auth import bp as auth_bp
from .routes.home import bp as home_bp
from .routes.profile import bp as profile_bp
from .routes.semesters import bp as semesters_bp
from .routes.aid import bp as aid_bp
from .routes.transactions import bp as transactions_bp
from .routes.categories import bp as categories_bp
from .routes.dashboard import bp as dashboard_bp
from .routes.parent_access import bp as parent_access_bp
from .routes.faqs import bp as faqs_bp
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or "dev_fallback",
        DATABASE="bag.sqlite3",
    )

    init_db_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(semesters_bp)
    app.register_blueprint(aid_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(parent_access_bp)
    app.register_blueprint(faqs_bp)

    @app.context_processor
    def inject_user_profile():
        display_name = "Bag User"
        avatar_letter = "B"
        nav_profile_image = None

        user_id = session.get("user_id")

        if user_id:
            db = get_db()
            row = db.execute(
                "SELECT display_name, profile_image FROM profiles WHERE user_id = ?",
                (user_id,),
            ).fetchone()

            if row:
                if row["display_name"] and row["display_name"].strip():
                    display_name = row["display_name"].strip()
                    avatar_letter = display_name[0].upper()

                if row["profile_image"] and row["profile_image"].strip():
                    saved_image = row["profile_image"].strip()

                    if saved_image.startswith("uploads/"):
                        nav_profile_image = f"/static/{saved_image}"
                    else:
                        nav_profile_image = f"/static/images/logos/{saved_image}"

        return {
            "nav_display_name": display_name,
            "nav_avatar_letter": avatar_letter,
            "nav_profile_image": nav_profile_image,
        }

    return app