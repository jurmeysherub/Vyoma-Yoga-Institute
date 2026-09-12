from app import app, db, ScheduleEntry, PricingPlan

with app.app_context():

    # Only seed if the tables are actually empty — prevents duplicate
    # entries if you accidentally run this file more than once
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
    print("Database seeded successfully.")