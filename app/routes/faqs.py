from flask import Blueprint, render_template
from app.auth import login_required

bp = Blueprint("faqs", __name__)

@bp.route("/faqs")
@login_required
def faqs():
    return render_template("faqs.html")