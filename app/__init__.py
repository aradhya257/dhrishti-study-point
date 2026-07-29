"""
Application factory for Dhrishti Study Point.
"""

import os

from flask import Flask
from flask_login import LoginManager

from config import Config
from app.models import db, Admin


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access the admin panel."
login_manager.login_message_category = "warning"


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    # --- Blueprints ---
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # --- Template globals: study point info available on every page ---
    @app.context_processor
    def inject_study_point_info():
        return {
            "STUDY_POINT_NAME": app.config["STUDY_POINT_NAME"],
            "STUDY_POINT_TAGLINE": app.config["STUDY_POINT_TAGLINE"],
            "STUDY_POINT_ADDRESS_LINES": app.config["STUDY_POINT_ADDRESS_LINES"],
            "STUDY_POINT_PHONE": app.config["STUDY_POINT_PHONE"],
            "STUDY_POINT_EMAIL": app.config["STUDY_POINT_EMAIL"],
            "GOOGLE_MAP_EMBED_URL": app.config["GOOGLE_MAP_EMBED_URL"],
        }

    # --- Create tables automatically on first run (safe if they already exist) ---
    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))
