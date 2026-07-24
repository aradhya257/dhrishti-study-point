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
# Helper: keep the seats table in sync with TOTAL_SEATS from config
# ---------------------------------------------------------------------------
def _ensure_seats_exist():
    total = current_app.config["TOTAL_SEATS"]
    existing = {s.seat_no for s in Seat.query.all()}
    for n in range(1, total + 1):
        if n not in existing:
            db.session.add(Seat(seat_no=n, status="available"))
    if db.session.new:
        db.session.commit()


@main_bp.route("/")
def home():
    _ensure_seats_exist()
    total_seats = Seat.query.count()
    available_seats = Seat.query.filter_by(status="available").count()
    return render_template(
        "index.html",
        page_title="Dhrishti Study Point – Best Self Study Library in Varanasi",
        meta_description=(
            "Dhrishti Study Point is a silent self study space in Salarpur, "
            "near Mata Mai Mandir, Varanasi. Find a quiet study room in Varanasi "
            "with WiFi, AC and comfortable seating."
        ),
        total_seats=total_seats,
        available_seats=available_seats,
    )


@main_bp.route("/about")
def about():
    return render_template(
        "about.html",
        page_title="About Us – Dhrishti Study Point, Varanasi",
        meta_description=(
            "Learn about Dhrishti Study Point, a silent study space near Mata Mai "
            "Mandir, Salarpur, Varanasi, built for focused self study and exam preparation."
        ),
    )


@main_bp.route("/facilities")
def facilities():
    return render_template(
        "facilities.html",
        page_title="Facilities – Dhrishti Study Point, Varanasi",
        meta_description=(
            "WiFi, silent environment, individual seating, AC and more at Dhrishti "
            "Study Point, the best study room in Varanasi."
        ),
    )


@main_bp.route("/seats")
def seats():
    _ensure_seats_exist()
    all_seats = Seat.query.order_by(Seat.seat_no).all()
    available_seats = sum(1 for s in all_seats if s.status == "available")
    return render_template(
        "seats.html",
        page_title="Seat Availability – Dhrishti Study Point, Varanasi",
        meta_description=(
            "Check live seat availability at Dhrishti Study Point, a silent study "
            "space near me in Varanasi."
        ),
        all_seats=all_seats,
        available_seats=available_seats,
        total_seats=len(all_seats),
    )


@main_bp.route("/fees")
def fees():
    return render_template(
        "fees.html",
        page_title="Fee Structure – Dhrishti Study Point, Varanasi",
        meta_description=(
            "Affordable monthly fee plans for the silent study space at Dhrishti "
            "Study Point, Salarpur, Varanasi."
        ),
    )


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not message:
            flash("Please fill in your name and message.", "danger")
        else:
            db.session.add(
                ContactMessage(name=name, mobile=mobile, email=email, message=message)
            )
            db.session.commit()
            flash("Thank you! Your message has been sent. We will contact you soon.", "success")
            return redirect(url_for("main.contact"))

    return render_template(
        "contact.html",
        page_title="Contact Us – Dhrishti Study Point, Varanasi",
        meta_description=(
            "Get in touch with Dhrishti Study Point, Salarpur, near Mata Mai Mandir, "
            "Varanasi. Visit us or send a message to book your seat."
        ),
    )


@main_bp.route("/flyer")
def flyer():
    return render_template(
        "flyer.html",
        page_title="Flyer – Dhrishti Study Point, Varanasi",
        meta_description="Download the Dhrishti Study Point flyer with facilities, address and contact details.",
    )


@main_bp.route("/register", methods=["GET", "POST"])
def register():
    """Optional public self-registration form (creates an unassigned, unpaid student record)."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        mobile = request.form.get("mobile", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not mobile:
            flash("Name and mobile number are required.", "danger")
        else:
            student = Student(name=name, mobile=mobile, email=email, fee_status="Unpaid")
            db.session.add(student)
            db.session.commit()
            flash(
                "Registration received! Please visit Dhrishti Study Point to complete "
                "payment and seat assignment.",
                "success",
            )
            return redirect(url_for("main.register"))

    return render_template(
        "register.html",
        page_title="Online Registration – Dhrishti Study Point, Varanasi",
        meta_description="Register online for a seat at Dhrishti Study Point, Varanasi.",
    )
