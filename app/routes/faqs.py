# BAG — Budgeting Aid Guide
# Copyright © 2026 Group_0
# All Rights Reserved

from flask import Blueprint, render_template
from app.auth import login_required

bp = Blueprint("faqs", __name__)


@bp.route("/faqs")
@login_required
def faqs():
    return render_template("faqs.html", active_tab="about-bag")


@bp.route("/faq/help")
@login_required
def faq_help():
    return render_template("faqs.html", active_tab="help-section")
