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


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Student Management
# ---------------------------------------------------------------------------
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
        students_query = students_query.filter_by(fee_status=fee_filter)

    all_students = students_query.order_by(Student.id.desc()).all()

    return render_template(
        "admin/students.html",
        page_title="Manage Students – Dhrishti Study Point",
        students=all_students,
        query=query,
        fee_filter=fee_filter,
    )


@admin_bp.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    _ensure_seats_exist()
    available_seats = Seat.query.filter_by(status="available").order_by(Seat.seat_no).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        seat_no = request.form.get("seat_no") or None
        fee_status = request.form.get("fee_status", "Unpaid")
        fee_amount = request.form.get("fee_amount", 500)
        join_date_str = request.form.get("join_date")

        if not name or not mobile:
            flash("Name and mobile number are required.", "danger")
            return redirect(url_for("admin.add_student"))

        join_date_val = (
            datetime.strptime(join_date_str, "%Y-%m-%d").date() if join_date_str else date.today()
        )

        student = Student(
            name=name,
            mobile=mobile,
            email=email,
            join_date=join_date_val,
            seat_no=int(seat_no) if seat_no else None,
            fee_status=fee_status,
            fee_amount=int(fee_amount) if fee_amount else 0,
        )
        db.session.add(student)

        if seat_no:
            seat = Seat.query.get(int(seat_no))
            if seat:
                seat.status = "occupied"

        db.session.commit()
        flash(f"Student '{name}' added successfully.", "success")
        return redirect(url_for("admin.students"))

    return render_template(
        "admin/student_form.html",
        page_title="Add Student – Dhrishti Study Point",
        student=None,
        available_seats=available_seats,
        today=date.today().isoformat(),
    )


@admin_bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    _ensure_seats_exist()

    # Seats available for selection = currently available + the seat this student already has
    available_seats = Seat.query.filter(
        db.or_(Seat.status == "available", Seat.seat_no == student.seat_no)
    ).order_by(Seat.seat_no).all()

    if request.method == "POST":
        old_seat_no = student.seat_no

        student.name = request.form.get("name", "").strip()
        student.mobile = request.form.get("mobile", "").strip()
        student.email = request.form.get("email", "").strip()
        new_seat_no = request.form.get("seat_no") or None
        student.fee_status = request.form.get("fee_status", "Unpaid")
        student.fee_amount = int(request.form.get("fee_amount") or 0)
        join_date_str = request.form.get("join_date")
        if join_date_str:
            student.join_date = datetime.strptime(join_date_str, "%Y-%m-%d").date()

        new_seat_no = int(new_seat_no) if new_seat_no else None

        if new_seat_no != old_seat_no:
            if old_seat_no:
                old_seat = Seat.query.get(old_seat_no)
                if old_seat:
                    old_seat.status = "available"
            if new_seat_no:
                new_seat = Seat.query.get(new_seat_no)
                if new_seat:
                    new_seat.status = "occupied"
            student.seat_no = new_seat_no

        db.session.commit()
        flash(f"Student '{student.name}' updated successfully.", "success")
        return redirect(url_for("admin.students"))

    return render_template(
        "admin/student_form.html",
        page_title="Edit Student – Dhrishti Study Point",
        student=student,
        available_seats=available_seats,
        today=date.today().isoformat(),
    )


@admin_bp.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    # Free up the seat
    if student.seat_no:
        seat = Seat.query.get(student.seat_no)
        if seat:
            seat.status = "available"

    db.session.delete(student)
    db.session.commit()
    flash(f"Student '{student.name}' deleted.", "info")
    return redirect(url_for("admin.students"))


@admin_bp.route("/students/<int:student_id>/toggle-fee", methods=["POST"])
@login_required
def toggle_fee(student_id):
    student = Student.query.get_or_404(student_id)
    student.fee_status = "Paid" if student.fee_status == "Unpaid" else "Unpaid"
    db.session.commit()
    flash(f"Fee status for '{student.name}' set to {student.fee_status}.", "success")
    return redirect(request.referrer or url_for("admin.students"))


# ---------------------------------------------------------------------------
# Fee Management
# ---------------------------------------------------------------------------
@admin_bp.route("/fees")
@login_required
def fee_management():
    filter_status = request.args.get("fee_status", "").strip()
    students_query = Student.query.filter_by(is_active=True)
    if filter_status in ("Paid", "Unpaid"):
        students_query = students_query.filter_by(fee_status=filter_status)
    all_students = students_query.order_by(Student.name).all()

    total_paid = Student.query.filter_by(is_active=True, fee_status="Paid").count()
    total_unpaid = Student.query.filter_by(is_active=True, fee_status="Unpaid").count()

    return render_template(
        "admin/fees.html",
        page_title="Fee Management – Dhrishti Study Point",
        students=all_students,
        filter_status=filter_status,
        total_paid=total_paid,
        total_unpaid=total_unpaid,
    )


# ---------------------------------------------------------------------------
# Attendance Management
# ---------------------------------------------------------------------------
@admin_bp.route("/attendance", methods=["GET", "POST"])
@login_required
def attendance():
    selected_date_str = request.args.get("date") or date.today().isoformat()
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = date.today()

    all_students = Student.query.filter_by(is_active=True).order_by(Student.name).all()

    existing_records = {
        a.student_id: a
        for a in Attendance.query.filter_by(date=selected_date).all()
    }

    if request.method == "POST":
        for student in all_students:
            status = request.form.get(f"status_{student.id}")
            if not status:
                continue
            record = existing_records.get(student.id)
            if record:
                record.status = status
            else:
                db.session.add(
                    Attendance(student_id=student.id, date=selected_date, status=status)
                )
        db.session.commit()
        flash(f"Attendance saved for {selected_date.strftime('%d %b %Y')}.", "success")
        return redirect(url_for("admin.attendance", date=selected_date.isoformat()))

    return render_template(
        "admin/attendance.html",
        page_title="Attendance – Dhrishti Study Point",
        students=all_students,
        existing_records=existing_records,
        selected_date=selected_date,
    )


# ---------------------------------------------------------------------------
# Contact messages (from public contact form)
# ---------------------------------------------------------------------------
@admin_bp.route("/messages")
@login_required
def messages():
    all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    for m in all_messages:
        m.is_read = True
    db.session.commit()
    return render_template(
        "admin/messages.html",
        page_title="Contact Messages – Dhrishti Study Point",
        messages=all_messages,
    )


# ---------------------------------------------------------------------------
# Search API (used by the live search box, optional AJAX endpoint)
# ---------------------------------------------------------------------------
@admin_bp.route("/api/search-students")
@login_required
def search_students_api():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        like = f"%{query}%"
        matched = Student.query.filter(
            db.and_(
                Student.is_active == True,  # noqa: E712
                db.or_(Student.name.ilike(like), Student.mobile.ilike(like)),
            )
        ).limit(10).all()
        results = [
            {
                "id": s.id,
                "name": s.name,
                "mobile": s.mobile,
                "seat_no": s.seat_no,
                "fee_status": s.fee_status,
            }
            for s in matched
        ]
    return jsonify(results)
