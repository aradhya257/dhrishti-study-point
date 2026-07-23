"""
One-time setup script:
  - Creates all database tables (if they don't already exist)
  - Creates the initial admin account (from ADMIN_USERNAME / ADMIN_PASSWORD
    environment variables, or safe defaults for local dev)
  - Creates the seats (count controlled by TOTAL_SEATS)

Usage:
    python seed.py
"""

import os

from app import create_app
from app.models import Admin, Seat, db


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        # --- Admin account ---
        username = app.config["ADMIN_USERNAME"]
        password = app.config["ADMIN_PASSWORD"]

        admin = Admin.query.filter_by(username=username).first()
        if admin is None:
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)
            print(f"[seed] Created admin account '{username}'.")
        else:
            print(f"[seed] Admin account '{username}' already exists — skipping.")

        # --- Seats ---
        total_seats = app.config["TOTAL_SEATS"]
        existing = {s.seat_no for s in Seat.query.all()}
        created = 0
        for n in range(1, total_seats + 1):
            if n not in existing:
                db.session.add(Seat(seat_no=n, status="available"))
                created += 1
        if created:
            print(f"[seed] Created {created} new seat(s).")
        else:
            print("[seed] Seats already exist — skipping.")

        db.session.commit()
        print("[seed] Done.")

        if password == "ChangeThisPassword123":
            print(
                "\n[seed] WARNING: You are using the default admin password. "
                "Set ADMIN_PASSWORD as an environment variable before deploying "
                "to production."
            )


if __name__ == "__main__":
    run()
