from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from werkzeug.utils import secure_filename
from app.auth import login_required
from app.common.constants import US_STATE_ABBREVIATIONS, PROFILE_IMAGE_CHOICES
from app.common.session_utils import current_user_id
from app.db import get_db
import os
import uuid

bp = Blueprint("profile", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    uid = current_user_id()
    row = db.execute("SELECT * FROM profiles WHERE user_id = ?", (uid,)).fetchone()

    if request.method == "POST":
        display_name = (request.form.get("display_name") or "").strip()
        state = (request.form.get("state") or "").strip()
        school = (request.form.get("school") or "").strip()
        student_status = (request.form.get("student_status") or "").strip()
        profile_image = (request.form.get("profile_image") or "").strip()
        weeks = request.form.get("default_semester_weeks") or "16"

        uploaded_file = request.files.get("custom_profile_photo")

        try:
            weeks_i = int(weeks)
        except Exception:
            weeks_i = 16

        if weeks_i < 8 or weeks_i > 26:
            flash("Default semester weeks must be between 8 and 26.")
            return render_template(
                "profile.html",
                profile=row,
                states=US_STATE_ABBREVIATIONS,
                profile_image_choices=PROFILE_IMAGE_CHOICES,
            )

        if student_status not in ("", "Full-time", "Part-time"):
            flash("Please choose a valid student status.")
            return render_template(
                "profile.html",
                profile=row,
                states=US_STATE_ABBREVIATIONS,
                profile_image_choices=PROFILE_IMAGE_CHOICES,
            )

        allowed_images = set(PROFILE_IMAGE_CHOICES + [""])

        # If a custom file was uploaded, it wins over preset selection
        if uploaded_file and uploaded_file.filename:
            if not allowed_file(uploaded_file.filename):
                flash("Please upload a valid image file (png, jpg, jpeg, gif, or webp).")
                return render_template(
                    "profile.html",
                    profile=row,
                    states=US_STATE_ABBREVIATIONS,
                    profile_image_choices=PROFILE_IMAGE_CHOICES,
                )

            filename = secure_filename(uploaded_file.filename)
            ext = filename.rsplit(".", 1)[1].lower()
            unique_filename = f"user_{uid}_{uuid.uuid4().hex}.{ext}"

            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "profile_photos",
            )
            os.makedirs(upload_folder, exist_ok=True)

            uploaded_file.save(os.path.join(upload_folder, unique_filename))
            profile_image = f"uploads/profile_photos/{unique_filename}"

        elif profile_image not in allowed_images and not profile_image.startswith("uploads/profile_photos/"):
            profile_image = ""

        db.execute(
            """
            INSERT INTO profiles (
                user_id,
                display_name,
                state,
                school,
                student_status,
                profile_image,
                default_semester_weeks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                display_name=excluded.display_name,
                state=excluded.state,
                school=excluded.school,
                student_status=excluded.student_status,
                profile_image=excluded.profile_image,
                default_semester_weeks=excluded.default_semester_weeks
            """,
            (uid, display_name, state, school, student_status, profile_image, weeks_i),
        )
        db.commit()
        flash("Profile saved.")
        return redirect(url_for("profile.profile"))

    return render_template(
        "profile.html",
        profile=row,
        states=US_STATE_ABBREVIATIONS,
        profile_image_choices=PROFILE_IMAGE_CHOICES,
    )