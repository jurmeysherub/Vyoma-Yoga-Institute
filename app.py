from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import csv
import io
import os
import smtplib
from email.mime.text import MIMEText
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyoma.db'
db = SQLAlchemy(app)

# ===== EMAIL NOTIFICATION SETTINGS =====
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')
RECEIVER_EMAIL = 'sonam@vyomayogainstitute.com'


def send_notification_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    except Exception as e:
        print(f"Failed to send notification email: {e}")

        
SCHEDULE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=0&single=true&output=csv"
PRICING_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=493372854&single=true&output=csv"
EVENTS_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=1413253241&single=true&output=csv"
BLOG_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=1722890409&single=true&output=csv"


def fetch_csv_rows(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.text))
    return [{k.strip().lower(): v.strip() for k, v in row.items()} for row in reader]


# ===== DATABASE MODELS =====
class ScheduleEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(30), nullable=False)
    class_name = db.Column(db.String(50), nullable=False)


class OnlineClassRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    class_type = db.Column(db.String(20), nullable=False)
    preferred_time = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text)


class PricingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    option = db.Column(db.String(50), nullable=False)
    fee = db.Column(db.String(30), nullable=False)
    validity = db.Column(db.String(30))
    category = db.Column(db.String(20), default='adult')


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


class FeedbackMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=False)


# ===== AUTOMATIC DATABASE SETUP FOR RENDER =====
# This tells Flask to build the database files and tables automatically on startup
with app.app_context():
    db.create_all()
# ===== AUTOMATIC DATABASE SETUP AND SEEDING FOR RENDER =====
# This creates the tables AND inserts your schedule/pricing automatically on startup
with app.app_context():
    db.create_all()  # Creates the missing tables
    
    # 1. Automatically seed Schedule data if it's empty
    if ScheduleEntry.query.count() == 0:
        schedule_data = [
            ("07:00-08:00 AM", "Monday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Tuesday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Wednesday", "B"),
            ("07:00-08:00 AM", "Thursday", "Qi Gong"),
            ("07:00-08:00 AM", "Friday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Saturday", "Hatha Yoga"),
            ("07:00-08:00 AM", "Sunday", "Hatha Yoga"),

            ("09:30-10:30 AM", "Monday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Tuesday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Wednesday", "R"),
            ("09:30-10:30 AM", "Thursday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Friday", "Hatha Yoga"),
            ("09:30-10:30 AM", "Saturday", "Kids Yoga"),
            ("09:30-10:30 AM", "Sunday", "Vyoma Wellness"),

            ("03:00-04:00 PM", "Monday", "Hatha Yoga"),
            ("03:00-04:00 PM", "Tuesday", "Power Yoga"),
            ("03:00-04:00 PM", "Wednesday", "E"),
            ("03:00-04:00 PM", "Thursday", "Core Yoga"),
            ("03:00-04:00 PM", "Friday", "Power Yoga"),
            ("03:00-04:00 PM", "Saturday", "Hatha Yoga"),
            ("03:00-04:00 PM", "Sunday", "Core Yoga"),

            ("06:00-07:00 PM", "Monday", "Power Yoga"),
            ("06:00-07:00 PM", "Tuesday", "Hatha Yoga"),
            ("06:00-07:00 PM", "Wednesday", "A"),
            ("06:00-07:00 PM", "Thursday", "Hatha Yoga"),
            ("06:00-07:00 PM", "Friday", "Core Yoga"),
            ("06:00-07:00 PM", "Saturday", "Hatha Yoga"),

            ("07:30-08:30 PM", "Monday", "Qi Gong"),
            ("07:30-08:30 PM", "Tuesday", "Hatha Yoga"),
            ("07:30-08:30 PM", "Wednesday", "K"),
            ("07:30-08:30 PM", "Thursday", "Hatha Yoga"),
            ("07:30-08:30 PM", "Friday", "Hatha Yoga"),
        ]
        for time_slot, day, class_name in schedule_data:
            db.session.add(ScheduleEntry(time_slot=time_slot, day=day, class_name=class_name))

    # 2. Automatically seed Pricing data if it's empty
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
            db.session.add(PricingPlan(option=option, fee=fee, validity=validity, category=category))

    db.session.commit()
    print("Database auto-seeded successfully on startup.")


# ===== HOME =====
@app.route('/')
def home():
    return render_template('index.html', hero_class='')


# ===== CLASSES =====
@app.route('/classes')
def classes():
    return render_template('classes.html', hero_class='hero-banner-short hero-banner-classes')


# ===== SCHEDULE =====
@app.route('/schedule')
def schedule():
    try:
        schedule_rows = fetch_csv_rows(SCHEDULE_CSV_URL)
    except Exception:
        schedule_rows = []

    grid = {}
    time_slots = []
    for row in schedule_rows:
        slot = row.get('time slot', '')
        day = row.get('day', '')
        class_name = row.get('class', '')
        grid.setdefault(slot, {})[day] = class_name
        if slot not in time_slots:
            time_slots.append(slot)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return render_template('schedule.html', grid=grid, days=days, time_slots=time_slots,
                            hero_class='hero-banner-short hero-banner-schedule')


# ===== PRICING =====
@app.route('/pricing')
def pricing():
    try:
        pricing_rows = fetch_csv_rows(PRICING_CSV_URL)
    except Exception:
        pricing_rows = []

    adult_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'adult']
    kids_pricing = [r for r in pricing_rows if r.get('category', '').lower() == 'kids']

    return render_template('pricing.html', adult_pricing=adult_pricing, kids_pricing=kids_pricing,
                            hero_class='hero-banner-short hero-banner-pricing')


# ===== ABOUT =====
@app.route('/about')
def about():
    return render_template('about.html', hero_class='hero-banner-short hero-banner-about')


# ===== CONTACT =====
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()

        send_notification_email(
            subject=f"New website message from {name}",
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        )

        return redirect(url_for('contact'))

    return render_template('contact.html', hero_class='hero-banner-short hero-banner-contact')



# ===== FEEDBACK =====
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name', '')
        rating = request.form['rating']
        comments = request.form['comments']

        new_feedback = FeedbackMessage(name=name, rating=rating, comments=comments)
        db.session.add(new_feedback)
        db.session.commit()

        send_notification_email(
            subject=f"New feedback submitted ({rating}/5 stars)",
            body=f"Name: {name or 'Anonymous'}\nRating: {rating}/5\n\nComments:\n{comments}"
        )

        return redirect(url_for('feedback'))

    return render_template('feedback.html', hero_class='hero-banner-short hero-banner-page')


# ===== TTC =====
@app.route('/ttc')
def ttc():
    return render_template('ttc.html', hero_class='hero-banner-short hero-banner-page')


# ===== EVENTS =====
@app.route('/events')
def events():
    try:
        events_rows = fetch_csv_rows(EVENTS_CSV_URL)
    except Exception:
        events_rows = []

    return render_template('events.html', events=events_rows,
                            hero_class='hero-banner-short hero-banner-page')


# ===== BLOG =====
@app.route('/blog')
def blog():
    try:
        blog_rows = fetch_csv_rows(BLOG_CSV_URL)
    except Exception:
        blog_rows = []

    return render_template('blog.html', posts=blog_rows,
                            hero_class='hero-banner-short hero-banner-page')


# ===== FAQ =====
@app.route('/faq')
def faq():
    return render_template('faq.html', hero_class='hero-banner-short hero-banner-page')


# ===== ONLINE CLASS REQUEST =====
@app.route('/online-request', methods=['POST'])
def online_request():
    name = request.form['name']
    email = request.form['email']
    class_type = request.form['class_type']
    preferred_time = request.form['preferred_time']
    message = request.form.get('message', '')

    new_request = OnlineClassRequest(
        name=name, email=email, class_type=class_type,
        preferred_time=preferred_time, message=message
    )
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('schedule'))


    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for('schedule'))

from flask import Response

SITE_URL = "https://vyomayogainstitute.com"  # use your real live address

@app.route('/robots.txt')
def robots():
    return Response(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
                    mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    pages = ['home', 'classes', 'schedule', 'pricing', 'about',
             'contact', 'ttc', 'events', 'blog', 'faq', 'feedback']
    urls = ''.join(f"<url><loc>{SITE_URL}{url_for(p)}</loc></url>" for p in pages)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    return Response(xml, mimetype='application/xml')


if __name__ == '__main__':
    app.run(debug=True)





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




