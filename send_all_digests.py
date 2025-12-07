# send_all_digests.py

from db.database import SessionLocal
from db import models
from notifications.digest_builder import get_items_for_user
from notifications.email_renderer import render_digest
from notifications.email_sender import send_email
from notifications.geocoder import geocode


def main():
    db = SessionLocal()

    users = db.query(models.User).all()

    for user in users:

        # ----------------------------------------------------
        # 1. Ensure ALL user locations have geocodes (lazy load)
        # ----------------------------------------------------
        for loc in user.locations:
            if loc.lat is None or loc.lon is None:
                print(f"📍 Geocoding missing coords for '{loc.label}' ...")
                geo = geocode(db, loc.address)
                if geo:
                    loc.lat = geo["lat"]
                    loc.lon = geo["lon"]
                    loc.normalized_address = geo.get("normalized", loc.address)
        db.commit()

        # ----------------------------------------------------
        # 2. Get personalized relevant items 
        #    (topics + all saved locations)
        # ----------------------------------------------------
        items = get_items_for_user(db, user)

        if not items:
            print(f"ℹ No matching items for {user.email}; skipping.")
            continue

        # ----------------------------------------------------
        # 3. Render newsletter HTML
        # ----------------------------------------------------
        html_body = render_digest(user, items)

        # ----------------------------------------------------
        # 4. Send the email
        # ----------------------------------------------------
        send_email(
            to=user.email,
            subject="Your Civic Agenda Digest",
            html_body=html_body
        )

        print(f"📨 Sent digest to {user.email}")

    db.close()


if __name__ == "__main__":
    main()
