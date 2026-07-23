"""
WSGI entry point used by Gunicorn in production.

Gunicorn command (see Procfile / render.yaml):
    gunicorn wsgi:app
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
