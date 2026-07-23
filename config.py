"""
Configuration for Dhrishti Study Point.
All sensitive values are read from environment variables so nothing
secret is ever committed to GitHub. See .env.example for the full list.
"""

import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core Flask settings ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # --- Database ---
    # Example: mysql+pymysql://username:password@host:3306/dhrishti_study_point
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/dhrishti_study_point",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True, "pool_recycle": 280}

    # --- Session ---
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    # --- Seats ---
    TOTAL_SEATS = int(os.environ.get("TOTAL_SEATS", 40))

    # --- Default admin (used only by seed.py on first setup) ---
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeThisPassword123")

    # --- Study Point details (kept here so they're easy to edit) ---
    STUDY_POINT_NAME = "Dhrishti Study Point"
    STUDY_POINT_TAGLINE = "A Silent Place to Focus & Achieve"
    STUDY_POINT_ADDRESS_LINES = [
        "Dhrishti Study Point",
        "Salarpur, Near Mata Mai Mandir",
        "Varanasi, Uttar Pradesh, India",
    ]
    STUDY_POINT_PHONE = os.environ.get("STUDY_POINT_PHONE", "+91-8931848212")
    STUDY_POINT_EMAIL = os.environ.get("STUDY_POINT_EMAIL", "info@dhrishtistudypoint.com")
    # Replace with the real embed URL from Google Maps (Share > Embed a map)
    GOOGLE_MAP_EMBED_URL = os.environ.get(
        "GOOGLE_MAP_EMBED_URL",
        "https://www.google.com/maps?q=Mata+Mai+Mandir+Salarpur+Varanasi&output=embed",
    )
