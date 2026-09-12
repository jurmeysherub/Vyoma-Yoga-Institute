from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vyoma.db'
db = SQLAlchemy(app)


import csv
import io
import requests

SCHEDULE_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=0&single=true&output=csv"
PRICING_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRCr9sjgkC1JT5NqeVodceumml4g9Zr9zfQrHfnqVvW-4DIwlKcDFW18wzaWWc30iFDNKlyPv9XGERA/pub?gid=493372854&single=true&output=csv"

def fetch_csv_rows(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    reader = csv.DictReader(io.StringIO(response.text))
    # normalize keys to lowercase and strip extra whitespace, so
    # small typos in the sheet's spacing don't break anything
    return [{k.strip().lower(): v.strip() for k, v in row.items()} for row in reader]


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

# ===== HOME =====
@app.route('/')
def home():
    return render_template('index.html', hero_class='')


# ===== CLASSES (class types + schedule + online request) =====
@app.route('/classes')
def classes():
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

    return render_template('classes.html', grid=grid, days=days, time_slots=time_slots,
                            hero_class='hero-banner-short hero-banner-classes')

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


# ===== ABOUT (studio space + owners) =====
@app.route('/about')
def about():
    return render_template('about.html', hero_class='hero-banner-short hero-banner-about')




# ===== CONTACT (form + map) =====
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        new_message = ContactMessage(name=name, email=email, message=message)
        db.session.add(new_message)
        db.session.commit()

        return redirect(url_for('contact'))

    return render_template('contact.html', hero_class='hero-banner-short hero-banner-contact')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name', '')
        rating = request.form['rating']
        comments = request.form['comments']

        new_feedback = FeedbackMessage(name=name, rating=rating, comments=comments)
        db.session.add(new_feedback)
        db.session.commit()

        return redirect(url_for('feedback'))

    return render_template('feedback.html', hero_class='hero-banner-short hero-banner-page')


# ===== TTC =====
@app.route('/ttc')
def ttc():
    return render_template('ttc.html', hero_class='hero-banner-short hero-banner-page')


# Add these three routes to app.py, alongside your existing ones
# (placeholder pages for now — real content comes later)

@app.route('/events')
def events():
    return render_template('events.html', hero_class='hero-banner-short hero-banner-page')


@app.route('/coaching')
def coaching():
    return render_template('coaching.html', hero_class='hero-banner-short hero-banner-page')


@app.route('/faq')
def faq():
    return render_template('faq.html', hero_class='hero-banner-short hero-banner-page')

@app.route('/blog')
def blog():
    return render_template('blog.html', hero_class='hero-banner-short hero-banner-page')

# ===== ONLINE CLASS REQUEST (form lives on /classes now) =====
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

    return redirect(url_for('classes'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
