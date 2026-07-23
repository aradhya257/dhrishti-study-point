"""
SQLAlchemy models for Dhrishti Study Point.

Tables:
    admins      -> admin panel login accounts
    seats       -> physical seats in the study space
    students    -> student / member records
    attendance  -> daily attendance log per student
    contact_messages -> messages submitted via the public contact form
"""

from datetime import date, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Seat(db.Model):
    __tablename__ = "seats"

    seat_no = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default="available", nullable=False)  # available / occupied

    student = db.relationship("Student", backref="seat", uselist=False)

    def __repr__(self):
        return f"<Seat {self.seat_no} ({self.status})>"


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    join_date = db.Column(db.Date, default=date.today, nullable=False)
    seat_no = db.Column(db.Integer, db.ForeignKey("seats.seat_no"), nullable=True)
    fee_status = db.Column(db.String(20), default="Unpaid", nullable=False)  # Paid / Unpaid
    fee_amount = db.Column(db.Integer, default=500)
    fee_due_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)

    attendance_records = db.relationship(
        "Attendance", backref="student", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Student {self.name}>"


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    status = db.Column(db.String(20), default="Present", nullable=False)  # Present / Absent

    __table_args__ = (db.UniqueConstraint("student_id", "date", name="uix_student_date"),)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(120))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
