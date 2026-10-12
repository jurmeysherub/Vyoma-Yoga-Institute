from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import csv
import io
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

app = Flask(__name__)

# Change this to a long random secret in your .env file
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    'change-this-secret-key'
)

# =========================================================
# DATABASE
# =========================================================

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyoma.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# =========================================================
# EMAIL SETTINGS
# =========================================================

SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')

# Owner / receiver email
RECEIVER_EMAIL = 'sonam@vyomayogainstitute.com'


def send_notification_email(subject, body):
    """
    Send notification email to the owner.
    """

    if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
        print("Email settings are missing.")
        return False

    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)

            server.sendmail(
                SENDER_EMAIL,
                RECEIVER_EMAIL,
                msg.as_string()
            )

        print("Notification email sent successfully.")
        return True

    except Exception as e:
        print(f"Failed to send notification email: {e}")
        return False


# =========================================================
# OPTIONAL GOOGLE CSV SETTINGS
# =========================================================
#
# These are ONLY used for Events and Blog.
# Schedule and Pricing now use SQLite.
#

EVENTS_CSV_URL = os.environ.get('EVENTS_CSV_URL', '')
BLOG_CSV_URL = os.environ.get('BLOG_CSV_URL', '')


def fetch_csv_rows(url):
    """
    Fetch CSV data from a public URL.
    Used for Events and Blog.
    """

    if not url:
        return []

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        reader = csv.DictReader(
            io.StringIO(response.text)
        )

        return [
            {
                k.strip().lower(): v.strip()
                for k, v in row.items()
            }
            for row in reader
        ]

    except Exception as e:
        print(f"CSV error: {e}")
        return []


# =========================================================
# DATABASE MODELS
# =========================================================

class ScheduleEntry(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    day = db.Column(
        db.String(20),
        nullable=False
    )

    time_slot = db.Column(
        db.String(30),
        nullable=False
    )

    class_name = db.Column(
        db.String(50),
        nullable=False
    )


class OnlineClassRequest(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )

    class_type = db.Column(
        db.String(20),
        nullable=False
    )

    preferred_time = db.Column(
        db.String(100),
        nullable=False
    )

    message = db.Column(db.Text)


class PricingPlan(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    option = db.Column(
        db.String(50),
        nullable=False
    )

    fee = db.Column(
        db.String(30),
        nullable=False
    )

    validity = db.Column(
        db.String(30)
    )

    category = db.Column(
        db.String(20),
        default='adult'
    )


class ContactMessage(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )


class FeedbackMessage(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100)
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comments = db.Column(
        db.Text,
        nullable=False
    )


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():
    """
    Create database tables and add initial
    schedule/pricing data if the database is empty.
    """

    db.create_all()

    # -----------------------------------------------------
    # INITIAL SCHEDULE
    # -----------------------------------------------------

    if ScheduleEntry.query.count() == 0:

        schedule_data = [

            # 07:00 AM
            ("07:00-08:00 AM", "Monday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Tuesday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Wednesday", "B"),
            ("07:00-08:00 AM", "Thursday", "Qi Gong"),
            ("07:00-08:00 AM", "Friday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Saturday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Sunday", "Hatha Yoga"),

            # 09:30 AM
            ("09:30-10:30 AM", "Monday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Tuesday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Wednesday", "R"),
            ("09:30-10:30 AM", "Thursday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Friday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Saturday", "Kids Yoga"),
            ("09:30-10:30 AM", "Sunday", "Vyoma Wellness"),

            # 03:00 PM
            ("03:00-04:00 PM", "Monday", "Hatha Yoga"),
            ("03:00-04:00 PM", "Tuesday", "Power Yoga"),
            ("03:00-04:00 PM", "Wednesday", "E"),
            ("03:00-04:00 PM", "Thursday", "Core Yoga"),
            ("03:00-04:00 PM", "Friday", "Power Yoga"),
            ("03:00-04:00 PM", "Saturday", "Hatha Yoga"),
            ("03:00-04:00 PM", "Sunday", "Core Yoga"),

            # 06:00 PM
            ("06:00-07:00 PM", "Monday", "Power Yoga"),
            ("06:00-07:00 PM", "Tuesday", "Hatha Yoga"),
            ("06:00-07:00 PM", "Wednesday", "A"),
            ("06:00-07:00 PM", "Thursday", "Hatha Yoga"),
            ("06:00-07:00 PM", "Friday", "Core Yoga"),
            ("06:00-07:00 PM", "Saturday", "Hatha Yoga"),

            # 07:30 PM
            ("07:30-08:30 PM", "Monday", "Qi Gong"),
            ("07:30-08:30 PM", "Tuesday", "Hatha Yoga"),
            ("07:30-08:30 PM", "Wednesday", "K"),
            ("07:30-08:30 PM", "Thursday", "Hatha Yoga"),
            ("07:30-08:30 PM", "Friday", "Hatha Yoga"),
        ]

        for time_slot, day, class_name in schedule_data:

            db.session.add(
                ScheduleEntry(
                    time_slot=time_slot,
                    day=day,
                    class_name=class_name
                )
            )

    # -----------------------------------------------------
    # INITIAL PRICING
    # -----------------------------------------------------

    if PricingPlan.query.count() == 0:

        pricing_data = [

            ("Drop-In Class", "Nu. 500", "1 day", "adult"),
            ("10 Class Pass", "Nu. 3,000", "45 days", "adult"),
            ("Monthly Unlimited", "Nu. 8,500", "30 days", "adult"),
            ("6 Month Unlimited", "Nu. 42,000", "6 months", "adult"),

            ("Drop-In Class", "Nu. 400", None, "kids"),
            ("4 Class Pass", "Nu. 1,400", None, "kids"),
            ("8 Class Pass", "Nu. 2,500", None, "kids"),
        ]

        for option, fee, validity, category in pricing_data:

            db.session.add(
                PricingPlan(
                    option=option,
                    fee=fee,
                    validity=validity,
                    category=category
                )
            )

    db.session.commit()

    print("Database initialized successfully.")


# Run database initialization once
with app.app_context():
    initialize_database()


# =========================================================
# HOME
# =========================================================

@app.route('/')
def home():

    return render_template(
        'index.html',
        hero_class=''
    )


# =========================================================
# CLASSES
# =========================================================

@app.route('/classes')
def classes():

    return render_template(
        'classes.html',
        hero_class='hero-banner-short hero-banner-classes'
    )


# =========================================================
# SCHEDULE
# =========================================================

@app.route('/schedule')
def schedule():

    # Get schedule directly from SQLite
    schedule_rows = ScheduleEntry.query.all()

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    # Create the same grid structure
    # your existing schedule.html expects
    grid = {}

    time_slots = []

    for row in schedule_rows:

        slot = row.time_slot
        day = row.day
        class_name = row.class_name

        if slot not in grid:
            grid[slot] = {}

        grid[slot][day] = class_name

        if slot not in time_slots:
            time_slots.append(slot)

    return render_template(
        'schedule.html',
        grid=grid,
        days=days,
        time_slots=time_slots,
        hero_class='hero-banner-short hero-banner-schedule'
    )


# =========================================================
# PRICING
# =========================================================

@app.route('/pricing')
def pricing():

    # Get pricing directly from SQLite
    pricing_rows = PricingPlan.query.all()

    adult_pricing = [
        {
            'option': item.option,
            'fee': item.fee,
            'validity': item.validity,
            'category': item.category
        }
        for item in pricing_rows
        if item.category.lower() == 'adult'
    ]

    kids_pricing = [
        {
            'option': item.option,
            'fee': item.fee,
            'validity': item.validity,
            'category': item.category
        }
        for item in pricing_rows
        if item.category.lower() == 'kids'
    ]

    return render_template(
        'pricing.html',
        adult_pricing=adult_pricing,
        kids_pricing=kids_pricing,
        hero_class='hero-banner-short hero-banner-pricing'
    )


# =========================================================
# ABOUT
# =========================================================

@app.route('/about')
def about():

    return render_template(
        'about.html',
        hero_class='hero-banner-short hero-banner-about'
    )


# =========================================================
# CONTACT
# =========================================================

@app.route('/contact', methods=['GET', 'POST'])
def contact():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:

            flash(
                'Please fill in all required fields.',
                'error'
            )

            return redirect(url_for('contact'))

        # Save to database
        new_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        db.session.add(new_message)
        db.session.commit()

        # Send notification
        email_sent = send_notification_email(
            subject=f"New website message from {name}",
            body=(
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}"
            )
        )

        if email_sent:

            flash(
                'Thank you! Your message has been sent.',
                'success'
            )

        else:

            flash(
                'Your message was saved, but the email notification could not be sent.',
                'warning'
            )

        return redirect(url_for('contact'))

    return render_template(
        'contact.html',
        hero_class='hero-banner-short hero-banner-contact'
    )


# =========================================================
# FEEDBACK
# =========================================================

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()

        try:
            rating = int(request.form.get('rating', 0))
        except ValueError:
            rating = 0

        comments = request.form.get(
            'comments',
            ''
        ).strip()

        if rating < 1 or rating > 5:

            flash(
                'Please select a rating between 1 and 5.',
                'error'
            )

            return redirect(url_for('feedback'))

        if not comments:

            flash(
                'Please enter your feedback.',
                'error'
            )

            return redirect(url_for('feedback'))

        # Save feedback
        new_feedback = FeedbackMessage(
            name=name,
            rating=rating,
            comments=comments
        )

        db.session.add(new_feedback)
        db.session.commit()

        # Email notification
        email_sent = send_notification_email(
            subject=f"New feedback submitted ({rating}/5 stars)",
            body=(
                f"Name: {name or 'Anonymous'}\n"
                f"Rating: {rating}/5\n\n"
                f"Comments:\n{comments}"
            )
        )

        if email_sent:

            flash(
                'Thank you for your feedback!',
                'success'
            )

        else:

            flash(
                'Your feedback was saved, but the email notification could not be sent.',
                'warning'
            )

        return redirect(url_for('feedback'))

    return render_template(
        'feedback.html',
        hero_class='hero-banner-short hero-banner-page'
    )


# =========================================================
# TTC
# =========================================================

@app.route('/ttc')
def ttc():

    return render_template(
        'ttc.html',
        hero_class='hero-banner-short hero-banner-page'
    )


# =========================================================
# EVENTS
# =========================================================

@app.route('/events')
def events():

    events_rows = fetch_csv_rows(
        EVENTS_CSV_URL
    )

    return render_template(
        'events.html',
        events=events_rows,
        hero_class='hero-banner-short hero-banner-page'
    )


# =========================================================
# BLOG
# =========================================================

@app.route('/blog')
def blog():

    blog_rows = fetch_csv_rows(
        BLOG_CSV_URL
    )

    return render_template(
        'blog.html',
        posts=blog_rows,
        hero_class='hero-banner-short hero-banner-page'
    )


# =========================================================
# FAQ
# =========================================================

@app.route('/faq')
def faq():

    return render_template(
        'faq.html',
        hero_class='hero-banner-short hero-banner-page'
    )


# =========================================================
# ONLINE CLASS REQUEST
# =========================================================

@app.route('/online-request', methods=['POST'])
def online_request():

    name = request.form.get(
        'name',
        ''
    ).strip()

    email = request.form.get(
        'email',
        ''
    ).strip()

    class_type = request.form.get(
        'class_type',
        ''
    ).strip()

    preferred_time = request.form.get(
        'preferred_time',
        ''
    ).strip()

    message = request.form.get(
        'message',
        ''
    ).strip()

    if not name or not email or not class_type or not preferred_time:

        flash(
            'Please complete all required fields.',
            'error'
        )

        return redirect(url_for('schedule'))

    # Save request
    new_request = OnlineClassRequest(
        name=name,
        email=email,
        class_type=class_type,
        preferred_time=preferred_time,
        message=message
    )

    db.session.add(new_request)
    db.session.commit()

    # Notify owner
    send_notification_email(
        subject=f"New Online Class Request from {name}",
        body=(
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Class Type: {class_type}\n"
            f"Preferred Time: {preferred_time}\n\n"
            f"Message:\n{message or 'No message provided'}"
        )
    )

    flash(
        'Your online class request has been submitted.',
        'success'
    )

    return redirect(url_for('schedule'))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == '__main__':

    app.run(
        debug=True
    )















# from flask import Flask, render_template, request, redirect, url_for
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv
# import csv
# import io
# import os
# import smtplib
# from email.mime.text import MIMEText
# import requests

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyoma.db'
# db = SQLAlchemy(app)

# # ===== EMAIL NOTIFICATION SETTINGS =====
# SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
# SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')
# RECEIVER_EMAIL = 'sonam@vyomayogainstitute.com'


# def send_notification_email(subject, body):
#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = SENDER_EMAIL
#     msg['To'] = RECEIVER_EMAIL

#     try:
#         with smtplib.SMTP('://gmail.com', 587) as server:
#             server.starttls()
#             server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
#             server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
#     except Exception as e:
#         print(f"Failed to send notification email: {e}")

        
# SCHEDULE_CSV_URL = "https://google.com"
# PRICING_CSV_URL = "https://google.com"
# EVENTS_CSV_URL = "https://google.com"
# BLOG_CSV_URL = "https://google.com"


# def fetch_csv_rows(url):
#     response = requests.get(url, timeout=5)
#     response.raise_for_status()
#     reader = csv.DictReader(io.StringIO(response.text))
#     return [{k.strip().lower(): v.strip() for k, v in row.items()} for row in reader]


# # ===== DATABASE MODELS =====
# class ScheduleEntry(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     day = db.Column(db.String(20), nullable=False)
#     time_slot = db.Column(db.String(30), nullable=False)
#     class_name = db.Column(db.String(50), nullable=False)


# class OnlineClassRequest(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     class_type = db.Column(db.String(20), nullable=False)
#     preferred_time = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text)


# class PricingPlan(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     option = db.Column(db.String(50), nullable=False)
#     fee = db.Column(db.String(30), nullable=False)
#     validity = db.Column(db.String(30))
#     category = db.Column(db.String(20), default='adult')


# class ContactMessage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(100), nullable=False)
#     message = db.Column(db.Text, nullable=False)


# class FeedbackMessage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     rating = db.Column(db.Integer, nullable=False)
#     comments = db.Column(db.Text, nullable=False)


# # ===== AUTOMATIC DATABASE SETUP FOR RENDER =====
# # This tells Flask to build the database files and tables automatically on startup
# with app.app_context():
#     db.create_all()
# # ===== AUTOMATIC DATABASE SETUP AND SEEDING FOR RENDER =====
# # This creates the tables AND inserts your schedule/pricing automatically on startup
# with app.app_context():
#     db.create_all()  # Creates the missing tables
    
#     # 1. Automatically seed Schedule data if it's empty
#     if ScheduleEntry.query.count() == 0:
#         schedule_data = [
#             ("07:00-08:00 AM", "Monday", "Hatha Yoga"),
#             ("07:00-08:00 AM", "Tuesday", "Hatha Yoga"),
#             ("07:00-08:00 AM", "Wednesday", "B"),
#             ("07:00-08:00 AM", "Thursday", "Qi Gong"),
#             ("07:00-08:00 AM", "Friday", "Hatha Yoga"),
#             ("07:00-08:00 AM", "Saturday", "Hatha Yoga"),
#             ("07:00-08:00 AM", "Sunday", "Hatha Yoga"),

#             ("09:30-10:30 AM", "Monday", "Hatha Yoga"),
#             ("09:30-10:30 AM", "Tuesday", "Hatha Yoga"),
#             ("09:30-10:30 AM", "Wednesday", "R"),
#             ("09:30-10:30 AM", "Thursday", "Hatha Yoga"),
#             ("09:30-10:30 AM", "Friday", "Hatha Yoga"),
#             ("09:30-10:30 AM", "Saturday", "Kids Yoga"),
#             ("09:30-10:30 AM", "Sunday", "Vyoma Wellness"),

#             ("03:00-04:00 PM", "Monday", "Hatha Yoga"),
#             ("03:00-04:00 PM", "Tuesday", "Power Yoga"),
#             ("03:00-04:00 PM", "Wednesday", "E"),
#             ("03:00-04:00 PM", "Thursday", "Core Yoga"),
#             ("03:00-04:00 PM", "Friday", "Power Yoga"),
#             ("03:00-04:00 PM", "Saturday", "Hatha Yoga"),
#             ("03:00-04:00 PM", "Sunday", "Core Yoga"),

#             ("06:00-07:00 PM", "Monday", "Power Yoga"),
#             ("06:00-07:00 PM", "Tuesday", "Hatha Yoga"),
#             ("06:00-07:00 PM", "Wednesday", "A"),
#             ("06:00-07:00 PM", "Thursday", "Hatha Yoga"),
#             ("06:00-07:00 PM", "Friday", "Core Yoga"),
#             ("06:00-07:00 PM", "Saturday", "Hatha Yoga"),

#             ("07:30-08:30 PM", "Monday", "Qi Gong"),
#             ("07:30-08:30 PM", "Tuesday", "Hatha Yoga"),
#             ("07:30-08:30 PM", "Wednesday", "K"),
#             ("07:30-08:30 PM", "Thursday", "Hatha Yoga"),
#             ("07:30-08:30 PM", "Friday", "Hatha Yoga"),
#         ]
#         for time_slot, day, class_name in schedule_data:
#             db.session.add(ScheduleEntry(time_slot=time_slot, day=day, class_name=class_name))

#     # 2. Automatically seed Pricing data if it's empty
#     if PricingPlan.query.count() == 0:
#         pricing_data = [
#             ("Drop-In Class", "Nu. 500", "1 day", "adult"),
#             ("10 Class Pass", "Nu. 3,000", "45 days", "adult"),
#             ("Monthly Unlimited", "Nu. 8,500", "30 days", "adult"),
#             ("6 Month Unlimited", "Nu. 42,000", "6 months", "adult"),
#             ("Drop-In Class", "Nu. 400", None, "kids"),
#             ("4 Class Pass", "Nu. 1,400", None, "kids"),
#             ("8 Class Pass", "Nu. 2,500", None, "kids"),
#         ]
#         for option, fee, validity, category in pricing_data:
#             db.session.add(PricingPlan(option=option, fee=fee, validity=validity, category=category))

#     db.session.commit()
#     print("Database auto-seeded successfully on startup.")


# # ===== HOME =====
# @app.route('/')
# def home():
#     return render_template('index.html', hero_class='')


# # ===== CLASSES =====
# @app.route('/classes')
# def classes():
#     return render_template('classes.html', hero_class='hero-banner-short hero-banner-classes')


# # ===== SCHEDULE =====
# @app.route('/schedule')
# def schedule():
#     try:
#         schedule_rows = fetch_csv_rows(SCHEDULE_CSV_URL)
#     except Exception:
#         schedule_rows = []

#     grid = {}
#     time_slots = []
#     for row in schedule_rows:
#         slot = row.get('time slot', '')
#         day = row.get('day', '')
#         class_name = row.get('class', '')
#         grid.setdefault(slot, {})[day] = class_name
#         if slot not in time_slots:
#             time_slots.append(slot)

#     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

#     return render_template('schedule.html', grid=grid, days=days, time_slots=time_slots,
#                             hero_class='hero-banner-short hero-banner-schedule')


# # ===== PRICING =====
# @app.route('/pricing')
# def pricing():
#     try:
#         pricing_rows = fetch_csv_rows(PRICING_CSV_URL)
#     except Exception:
#         pricing_rows = []

#     adult_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'adult']
#     kids_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'kids']

#     return render_template('pricing.html', adult_pricing=adult_pricing, kids_pricing=kids_pricing,
#                             hero_class='hero-banner-short hero-banner-pricing')


# # ===== ABOUT =====
# @app.route('/about')
# def about():
#     return render_template('about.html', hero_class='hero-banner-short hero-banner-about')


# # ===== CONTACT =====
# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         message = request.form['message']

#         new_message = ContactMessage(name=name, email=email, message=message)
#         db.session.add(new_message)
#         db.session.commit()

#         send_notification_email(
#             subject=f"New website message from {name}",
#             body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
#         )

#         return redirect(url_for('contact'))

#     return render_template('contact.html', hero_class='hero-banner-short hero-banner-contact')


# # ===== FEEDBACK =====
# @app.route('/feedback', methods=['GET', 'POST'])
# def feedback():
#     if request.method == 'POST':
#         name = request.form.get('name', '')
#         rating = request.form['rating']
#         comments = request.form['comments']

#         new_feedback = FeedbackMessage(name=name, rating=rating, comments=comments)
#         db.session.add(new_feedback)
#         db.session.commit()

#         send_notification_email(
#             subject=f"New feedback submitted ({rating}/5 stars)",
#             body=f"Name: {name or 'Anonymous'}\nRating: {rating}/5\n\nComments:\n{comments}"
#         )

#         return redirect(url_for('feedback'))

#     return render_template('feedback.html', hero_class='hero-banner-short hero-banner-page')


# # ===== TTC =====
# @app.route('/ttc')
# def ttc():
#     return render_template('ttc.html', hero_class='hero-banner-short hero-banner-page')


# # ===== EVENTS =====
# @app.route('/events')
# def events():
#     try:
#         events_rows = fetch_csv_rows(EVENTS_CSV_URL)
#     except Exception:
#         events_rows = []

#     return render_template('events.html', events=events_rows,
#                             hero_class='hero-banner-short hero-banner-page')


# # ===== BLOG =====
# @app.route('/blog')
# def blog():
#     try:
#         blog_rows = fetch_csv_rows(BLOG_CSV_URL)
#     except Exception:
#         blog_rows = []

#     return render_template('blog.html', posts=blog_rows,
#                             hero_class='hero-banner-short hero-banner-page')


# # ===== FAQ =====
# @app.route('/faq')
# def faq():
#     return render_template('faq.html', hero_class='hero-banner-short hero-banner-page')


# # ===== ONLINE CLASS REQUEST =====
# @app.route('/online-request', methods=['POST'])
# def online_request():
#     name = request.form['name']
#     email = request.form['email']
#     class_type = request.form['class_type']
#     preferred_time = request.form['preferred_time']
#     message = request.form.get('message', '')

#     new_request = OnlineClassRequest(
#         name=name, email=email, class_type=class_type,
#         preferred_time=preferred_time, message=message
#     )
#     db.session.add(new_request)
#     db.session.commit()
#     return redirect(url_for('schedule'))








# # from dotenv import load_dotenv
# # load_dotenv()

# # from flask import Flask, render_template, request, redirect, url_for
# # from flask_sqlalchemy import SQLAlchemy

# # app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyoma.db'
# # db = SQLAlchemy(app)


# # import csv
# # import io
# # import os
# # import smtplib
# # from email.mime.text import MIMEText
# # import requests

# # # ===== EMAIL NOTIFICATION SETTINGS =====
# # SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
# # SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')
# # RECEIVER_EMAIL = 'sonam@vyomayogainstitute.com'


# # def send_notification_email(subject, body):
# #     msg = MIMEText(body)
# #     msg['Subject'] = subject
# #     msg['From'] = SENDER_EMAIL
# #     msg['To'] = RECEIVER_EMAIL

# #     try:
# #         with smtplib.SMTP('smtp.gmail.com', 587) as server:
# #             server.starttls()
# #             server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
# #             server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
# #     except Exception as e:
# #         print(f"Failed to send notification email: {e}")

        
# # SCHEDULE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=0&single=true&output=csv"
# # PRICING_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=493372854&single=true&output=csv"
# # EVENTS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=1413253241&single=true&output=csv"
# # BLOG_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=1722890409&single=true&output=csv"


# # def fetch_csv_rows(url):
# #     response = requests.get(url, timeout=5)
# #     response.raise_for_status()
# #     reader = csv.DictReader(io.StringIO(response.text))
# #     return [{k.strip().lower(): v.strip() for k, v in row.items()} for row in reader]


# # class ScheduleEntry(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     day = db.Column(db.String(20), nullable=False)
# #     time_slot = db.Column(db.String(30), nullable=False)
# #     class_name = db.Column(db.String(50), nullable=False)


# # class OnlineClassRequest(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     email = db.Column(db.String(100), nullable=False)
# #     class_type = db.Column(db.String(20), nullable=False)
# #     preferred_time = db.Column(db.String(100), nullable=False)
# #     message = db.Column(db.Text)


# # class PricingPlan(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     option = db.Column(db.String(50), nullable=False)
# #     fee = db.Column(db.String(30), nullable=False)
# #     validity = db.Column(db.String(30))
# #     category = db.Column(db.String(20), default='adult')


# # class ContactMessage(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100), nullable=False)
# #     email = db.Column(db.String(100), nullable=False)
# #     message = db.Column(db.Text, nullable=False)

# # class FeedbackMessage(db.Model):
# #     id = db.Column(db.Integer, primary_key=True)
# #     name = db.Column(db.String(100))
# #     rating = db.Column(db.Integer, nullable=False)
# #     comments = db.Column(db.Text, nullable=False)

# # # ===== HOME =====
# # @app.route('/')
# # def home():
# #     return render_template('index.html', hero_class='')


# # # ===== CLASSES (class types — detailed info) =====
# # @app.route('/classes')
# # def classes():
# #     return render_template('classes.html', hero_class='hero-banner-short hero-banner-classes')


# # # ===== SCHEDULE (timetable + short blurbs + online request) =====
# # @app.route('/schedule')
# # def schedule():
# #     try:
# #         schedule_rows = fetch_csv_rows(SCHEDULE_CSV_URL)
# #     except Exception:
# #         schedule_rows = []

# #     grid = {}
# #     time_slots = []
# #     for row in schedule_rows:
# #         slot = row.get('time slot', '')
# #         day = row.get('day', '')
# #         class_name = row.get('class', '')
# #         grid.setdefault(slot, {})[day] = class_name
# #         if slot not in time_slots:
# #             time_slots.append(slot)

# #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# #     return render_template('schedule.html', grid=grid, days=days, time_slots=time_slots,
# #                             hero_class='hero-banner-short hero-banner-schedule')

# # # ===== PRICING =====
# # @app.route('/pricing')
# # def pricing():
# #     try:
# #         pricing_rows = fetch_csv_rows(PRICING_CSV_URL)
# #     except Exception:
# #         pricing_rows = []

# #     adult_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'adult']
# #     kids_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'kids']

# #     return render_template('pricing.html', adult_pricing=adult_pricing, kids_pricing=kids_pricing,
# #                             hero_class='hero-banner-short hero-banner-pricing')


# # # ===== ABOUT (studio space + owners) =====
# # @app.route('/about')
# # def about():
# #     return render_template('about.html', hero_class='hero-banner-short hero-banner-about')


# # # ===== CONTACT (form + map) =====
# # @app.route('/contact', methods=['GET', 'POST'])
# # def contact():
# #     if request.method == 'POST':
# #         name = request.form['name']
# #         email = request.form['email']
# #         message = request.form['message']

# #         new_message = ContactMessage(name=name, email=email, message=message)
# #         db.session.add(new_message)
# #         db.session.commit()

# #         send_notification_email(
# #         subject=f"New website message from {name}",
# #         body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
# #         )

# #         return redirect(url_for('contact'))

# #     return render_template('contact.html', hero_class='hero-banner-short hero-banner-contact')

# # @app.route('/feedback', methods=['GET', 'POST'])
# # def feedback():
# #     if request.method == 'POST':
# #         name = request.form.get('name', '')
# #         rating = request.form['rating']
# #         comments = request.form['comments']

# #         new_feedback = FeedbackMessage(name=name, rating=rating, comments=comments)
# #         db.session.add(new_feedback)
# #         db.session.commit()

# #         send_notification_email(
# #             subject=f"New feedback submitted ({rating}/5 stars)",
# #             body=f"Name: {name or 'Anonymous'}\nRating: {rating}/5\n\nComments:\n{comments}"
# #         )

# #         return redirect(url_for('feedback'))

# #     return render_template('feedback.html', hero_class='hero-banner-short hero-banner-page')


# # # ===== TTC =====
# # @app.route('/ttc')
# # def ttc():
# #     return render_template('ttc.html', hero_class='hero-banner-short hero-banner-page')


# # # ===== EVENTS =====
# # @app.route('/events')
# # def events():
# #     try:
# #         events_rows = fetch_csv_rows(EVENTS_CSV_URL)
# #     except Exception:
# #         events_rows = []

# #     return render_template('events.html', events=events_rows,
# #                             hero_class='hero-banner-short hero-banner-page')

# # # ===== BLOG (Instagram/TikTok embeds, self-managed via Google Sheet) =====
# # @app.route('/blog')
# # def blog():
# #     try:
# #         blog_rows = fetch_csv_rows(BLOG_CSV_URL)
# #     except Exception:
# #         blog_rows = []

# #     return render_template('blog.html', posts=blog_rows,
# #                             hero_class='hero-banner-short hero-banner-page')

# # @app.route('/faq')
# # def faq():
# #     return render_template('faq.html', hero_class='hero-banner-short hero-banner-page')


# # # ===== ONLINE CLASS REQUEST (form lives on /schedule now) =====
# # @app.route('/online-request', methods=['POST'])
# # def online_request():
# #     name = request.form['name']
# #     email = request.form['email']
# #     class_type = request.form['class_type']
# #     preferred_time = request.form['preferred_time']
# #     message = request.form.get('message', '')

# #     new_request = OnlineClassRequest(
# #         name=name, email=email, class_type=class_type,
# #         preferred_time=preferred_time, message=message
# #     )
# #     db.session.add(new_request)
# #     db.session.commit()

# #     send_notification_email(
# #         subject=f"New online class request from {name}",
# #         body=f"Name: {name}\nEmail: {email}\nClass type: {class_type}\nPreferred time: {preferred_time}\n\nMessage:\n{message}"
# #     )

# #     return redirect(url_for('schedule'))

# # if __name__ == '__main__':
# #     with app.app_context():
# #         db.create_all()
# #     app.run(debug=True)




