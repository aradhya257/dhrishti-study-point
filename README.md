# Dhrishti Study Point – Self Study Space Management System

A full-stack web app for managing a silent self-study space located in
Salarpur, near Mata Mai Mandir, Varanasi, Uttar Pradesh, India.

*"Dhrishti Study Point – A Silent Place to Focus & Achieve"*

Public website (home, about, facilities, live seat availability, fees,
contact form) + a secure admin panel (student management, seat assignment,
fee tracking, daily attendance, search).

---

## Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | HTML, CSS (custom design system), Bootstrap 5, vanilla JS |
| Backend    | Python 3 + Flask                              |
| Database   | MySQL (via SQLAlchemy + PyMySQL)              |
| Auth       | Flask-Login (session-based admin login)       |
| Deployment | Render (or any host that runs Gunicorn)       |

---

## Folder Structure

```
dhrishti_study_point/
├── app/
│   ├── __init__.py            # App factory, blueprint registration
│   ├── models.py              # SQLAlchemy models (Admin, Student, Seat, Attendance, ContactMessage)
│   ├── routes/
│   │   ├── main.py            # Public website routes
│   │   ├── auth.py            # Login / logout
│   │   └── admin.py           # Admin panel routes
│   ├── templates/
│   │   ├── base.html          # Shared layout, nav, footer, dark/light toggle
│   │   ├── index.html, about.html, facilities.html,
│   │   │   seats.html, fees.html, contact.html, register.html
│   │   └── admin/
│   │       ├── _layout.html   # Admin shell + sidebar
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── students.html
│   │       ├── student_form.html
│   │       ├── attendance.html
│   │       ├── fees.html
│   │       └── messages.html
│   └── static/
│       ├── css/style.css
│       └── js/main.js
├── config.py                  # Reads settings from environment variables
├── run.py                     # Local dev entry point (python run.py)
├── wsgi.py                    # Production entry point (gunicorn wsgi:app)
├── seed.py                    # Creates tables, admin account, seats
├── schema.sql                 # Manual SQL schema (optional alternative to seed.py)
├── requirements.txt
├── Procfile                   # For Render/Heroku-style process definition
├── render.yaml                # Render Blueprint
├── .env.example
└── .gitignore
```

---

## Database Design

**students** — `id, name, mobile, email, join_date, seat_no (FK), fee_status, fee_amount, fee_due_date, is_active`
**seats** — `seat_no (PK), status (available/occupied)`
**attendance** — `id, student_id (FK), date, status (Present/Absent)`
**admins** — `id, username, password_hash, created_at`
**contact_messages** — `id, name, mobile, email, message, created_at, is_read`

See `schema.sql` for the full manual SQL, or just run `seed.py`, which calls
`db.create_all()` and creates the same tables automatically.

---

## Local Setup

### 1. Prerequisites
- Python 3.10+
- MySQL Server running locally (or a remote MySQL instance)

### 2. Clone & install
```bash
git clone <your-repo-url> dhrishti_study_point
cd dhrishti_study_point
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the database
```sql
CREATE DATABASE dhrishti_study_point CHARACTER SET utf8mb4;
```
(or run `mysql -u root -p < schema.sql` to create tables directly)

### 4. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env` and set at minimum:
```
SECRET_KEY=some-long-random-string
DATABASE_URL=mysql+pymysql://root:yourpassword@localhost:3306/dhrishti_study_point
ADMIN_USERNAME=admin
ADMIN_PASSWORD=a-strong-password
```
Flask does not auto-load `.env` — either `pip install python-dotenv` and add
`from dotenv import load_dotenv; load_dotenv()` at the top of `run.py`, or
export the variables in your shell before running:
```bash
export $(cat .env | xargs)   # macOS/Linux
```

### 5. Initialize the database (tables + admin account + seats)
```bash
python seed.py
```

### 6. Run the app
```bash
python run.py
```
Visit `http://localhost:5000` for the public site and
`http://localhost:5000/login` to log in to the admin panel with the
`ADMIN_USERNAME` / `ADMIN_PASSWORD` you set above.

---

## Admin Panel Features

- **Dashboard** — total students, seats available/occupied, paid/unpaid fee
  summary, present-today count, recent students, unread messages.
- **Students** — add, edit, delete, assign/reassign a seat, search by name
  or mobile number, filter by fee status.
- **Fee Management** — one-click toggle between Paid / Unpaid per student.
- **Attendance** — pick any date, mark each active student Present/Absent,
  save in bulk. Re-visiting a date shows previously saved records.
- **Messages** — view contact form submissions from the public site.

---

## Deployment (Render)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Dhrishti Study Point"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Provision a MySQL database.** Render's built-in database is Postgres,
   so use an external MySQL provider (PlanetScale, Railway, Aiven, Clever
   Cloud, or your own VPS) and copy its connection string.

3. **Create the Render Web Service**
   - New → Blueprint → select this repo (uses `render.yaml`), **or**
   - New → Web Service → connect the repo manually with:
     - Build command: `pip install -r requirements.txt && python seed.py`
     - Start command: `gunicorn wsgi:app`

4. **Set environment variables** in the Render dashboard:
   - `SECRET_KEY` (generate a random value)
   - `DATABASE_URL` → your MySQL connection string
   - `ADMIN_USERNAME`, `ADMIN_PASSWORD` → your real admin credentials
   - `TOTAL_SEATS`, `STUDY_POINT_PHONE`, `STUDY_POINT_EMAIL`,
     `GOOGLE_MAP_EMBED_URL` as needed

5. **Deploy.** Render runs the build command (which also seeds the admin
   account and seats via `seed.py`), then starts Gunicorn.

6. **Verify:** visit your Render URL, check the public pages, then log in
   at `/login` with your admin credentials.

> Never commit real credentials. `.env` is already in `.gitignore` —
> only `.env.example` (with placeholder values) should be in GitHub.

---

## SEO

- Page title: **"Dhrishti Study Point – Best Self Study Library in Varanasi"**
- Meta description and keyword-rich copy on every page (`silent study space
  near me`, `library in Varanasi`, `study room in Varanasi`)
- Semantic headings (`h1`/`h2`) on every page
- `robots.txt` and `sitemap.xml` generated automatically at `/robots.txt`
  and `/sitemap.xml`
- LocalBusiness structured data (JSON-LD) in `base.html`
- Full address displayed in the footer of every page and on the Contact page

---

## Optional / Future Enhancements

The current build focuses on the core feature set. These are natural next
additions if you want to extend it:

- **Email/SMS fee reminders** — integrate an email provider (e.g. Flask-Mail
  + SMTP) or an SMS gateway (e.g. Twilio) and add a scheduled job (e.g.
  APScheduler or a Render Cron Job) that emails/texts students with
  `fee_status == "Unpaid"`.
- **Export student data** — add an `/admin/export` route using `openpyxl`
  (Excel) or `reportlab`/`fpdf2` (PDF) to download the student list.
- **Live seat availability without page refresh** — poll
  `/admin/api/search-students`-style JSON endpoint from the seats page with
  `fetch()` on an interval, or add WebSockets (Flask-SocketIO) for true
  real-time updates.

---

## Default Credentials (change immediately)

Set via `.env` before running `seed.py`. Do not deploy with the example
default password (`ChangeThisPassword123`).
