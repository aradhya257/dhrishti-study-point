"""
Authentication routes for the admin panel.
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.models import Admin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            login_user(admin, remember=True)
            flash(f"Welcome back, {admin.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html", page_title="Admin Login – Dhrishti Study Point")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
