"""
Local development entry point.

Usage:
    python run.py

Reads FLASK_DEBUG / PORT from environment if set, otherwise defaults to
debug mode on port 5000. For production use gunicorn with wsgi.py instead
(see README.md).
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
