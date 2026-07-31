"""
Admin panel routes.
Everything in this blueprint requires a logged-in admin (see @login_required).
"""

from datetime import date, datetime

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required

from app.models import Attendance, ContactMessage, Seat, Student, db

admin_bp = Blueprint("admin", __name__)


def _ensure_seats_exist():
    total = current_app.config["TOTAL_SEATS"]
    existing = {s.seat_no for s in Seat.query.all()}
    for n in range(1, total + 1):
        if n not in existing:
            db.session.add(Seat(seat_no=n, status="available"))
    if db.session.new:
        db.session.commit()


@admin_bp.route("/")
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    _ensure_seats_exist()

    total_students = Student.query.filter_by(is_active=True).count()
    total_seats = Seat.query.count()
    available_seats = Seat.query.filter_by(status="available").count()
    paid_count = Student.query.filter_by(is_active=True, fee_status="Paid").count()
    unpaid_count = Student.query.filter_by(is_active=True, fee_status="Unpaid").count()

    today = date.today()
    present_today = Attendance.query.filter_by(date=today, status="Present").count()

    recent_students = (
        Student.query.filter_by(is_active=True).order_by(Student.id.desc()).limit(5).all()
    )
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()

    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard – Dhrishti Study Point",
        total_students=total_students,
        total_seats=total_seats,
        available_seats=available_seats,
        occupied_seats=total_seats - available_seats,
        paid_count=paid_count,
        unpaid_count=unpaid_count,
        present_today=present_today,
        recent_students=recent_students,
        unread_messages=unread_messages,
        today=today,
    )


@admin_bp.route("/students")
@login_required
def students():
    query = request.args.get("q", "").strip()
    fee_filter = request.args.get("fee_status", "").strip()

    students_query = Student.query.filter_by(is_active=True)

    if query:
        like = f"%{query}%"
        students_query = students_query.filter(
            db.or_(Student.name.ilike(like), Student.mobile.ilike(like))
        )

    if fee_filter in ("Paid", "Unpaid"):
