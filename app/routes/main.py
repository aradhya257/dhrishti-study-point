"""
Public-facing routes: Home, About, Facilities, Seats, Fees, Contact.
No login required for any route in this blueprint.
"""

from flask import Blueprint, Response, current_app, flash, redirect, render_template, request, url_for

from app.models import ContactMessage, Seat, Student, db

main_bp = Blueprint("main", __name__)


@main_bp.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.url_root.rstrip('/')}/sitemap.xml",
    ]
    return Response("\n".join(lines), mimetype="text/plain")


@main_bp.route("/sitemap.xml")
def sitemap_xml():
    pages = ["main.home", "main.about", "main.facilities", "main.seats", "main.fees", "main.contact", "main.register", "main.flyer"]
    urls = "".join(f"<url><loc>{request.url_root.rstrip('/')}{url_for(p)}</loc></url>" for p in pages)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype="application/xml")


# ---------------------------------------------------------------------------
# Helper: keep the seats table in
cat > app/routes/auth.py << 'EOF'
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
cat > app/routes/admin.py << 'EOF'
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
cat > app/templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ page_title or (STUDY_POINT_NAME ~ ' – Best Self Study Library in Varanasi') }}</title>
<meta name="description" content="{{ meta_description or 'Dhrishti Study Point is a silent self study space in Salarpur, near Mata Mai Mandir, Varanasi, Uttar Pradesh.' }}">
<meta name="keywords" content="silent study space near me, library in Varanasi, study room in Varanasi, self study library Varanasi, Dhrishti Study Point, Salarpur study room">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{{ page_title or STUDY_POINT_NAME }}">
<meta property="og:description" content="{{ meta_description or STUDY_POINT_TAGLINE }}">
<meta property="og:type" content="website">

<!-- Bootstrap 5 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<!-- Bootstrap Icons -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
<!-- Google Font -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- Local Business structured data for SEO -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "LibraryOrganization",
  "name": "Dhrishti Study Point",
  "description": "A silent self study space in Salarpur, near Mata Mai Mandir, Varanasi, Uttar Pradesh.",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "Salarpur, Near Mata Mai Mandir",
    "addressLocality": "Varanasi",
    "addressRegion": "Uttar Pradesh",
    "addressCountry": "IN"
  }
}
</script>
</head>
<body>

<nav class="navbar navbar-expand-lg sticky-top main-navbar">
  <div class="container">
    <a class="navbar-brand" href="{{ url_for('main.home') }}">
      <i class="bi bi-book-half"></i> {{ STUDY_POINT_NAME }}
    </a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMain">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navMain">
      <ul class="navbar-nav ms-auto align-items-lg-center gap-lg-2">
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.home') }}">Home</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.about') }}">About</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.facilities') }}">Facilities</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.seats') }}">Seat Availability</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.fees') }}">Fees</a></li>
        <li class="nav-item"><a class="nav-link" href="{{ url_for('main.contact') }}">Contact</a></li>
        <li class="nav-item">
          <a class="btn btn-sm btn-primary-brand ms-lg-2" href="{{ url_for('main.register') }}">Register</a>
        </li>
        <li class="nav-item">
          <button id="themeToggle" class="btn btn-sm btn-outline-secondary ms-lg-2" title="Toggle dark/light mode">
            <i class="bi bi-moon-stars-fill"></i>
          </button>
        </li>
      </ul>
    </div>
  </div>
</nav>

<main>
  <div class="container mt-3">
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ 'danger' if category=='danger' else category }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}
  </div>

  {% block content %}{% endblock %}
</main>

<footer class="site-footer mt-5">
  <div class="container py-5">
    <div class="row g-4">
      <div class="col-md-4">
        <h5><i class="bi bi-book-half"></i> {{ STUDY_POINT_NAME }}</h5>
        <p class="text-muted-light">{{ STUDY_POINT_TAGLINE }}</p>
      </div>
      <div class="col-md-4">
        <h6>Visit Us</h6>
        {% for line in STUDY_POINT_ADDRESS_LINES %}
          <p class="mb-1">{{ line }}</p>
        {% endfor %}
      </div>
      <div class="col-md-4">
        <h6>Quick Links</h6>
        <ul class="list-unstyled footer-links">
          <li><a href="{{ url_for('main.facilities') }}">Facilities</a></li>
          <li><a href="{{ url_for('main.seats') }}">Seat Availability</a></li>
          <li><a href="{{ url_for('main.fees') }}">Fee Structure</a></li>
          <li><a href="{{ url_for('main.contact') }}">Contact Us</a></li>
          <li><a href="{{ url_for('auth.login') }}">Admin Login</a></li>
        </ul>
      </div>
    </div>
    <hr>
    <p class="text-center mb-0 text-muted-light">&copy; {{ 2026 }} {{ STUDY_POINT_NAME }}. All rights reserved.</p>
  </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
{% block scripts %}{% endblock %}
</body>
</html>
