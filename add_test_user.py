from db.database import SessionLocal
from db import models
from notifications.geocoder import geocode


def main():
    db = SessionLocal()

    user = models.User(
        email="passtibet1@gmail.com",
        interested_topics=["marijuana_regulation", "education"],
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"✅ User created | ID={user.user_id} | {user.email}")

    saved_locations = [
        {
            "label": "Home",
            "address": "1785 North Academy Boulevard, Colorado Springs, CO",
            "radius": 5,
        },
        {
            "label": "Work",
            "address": "1234 Fake Ave, Colorado Springs, CO",
            "radius": 8,
        },
        {
            "label": "Commute Intersection",
            "address": "4321 Fake Intersection Rd, Colorado Springs, CO",
            "radius": 10,
        },
    ]

    for loc in saved_locations:

        geo = geocode(db, loc["address"])

        user_loc = models.UserLocation(
            user_id=user.user_id,
            label=loc["label"],
            address=loc["address"],
            normalized_address=geo["normalized"] if geo else loc["address"],
            lat=float(geo["lat"]) if geo else None,
            lon=float(geo["lon"]) if geo else None,
            radius_miles=float(loc["radius"]),
        )

        db.add(user_loc)
        db.commit()

        print(
            f"📍 Added '{loc['label']}' | "
            f"{loc['address']} | "
            f"radius={loc['radius']}mi | "
            f"geocoded={'YES' if geo else 'NO'}"
        )

    db.close()
    print("\n🎉 Test user + multiple saved locations successfully added!")


if __name__ == "__main__":
    main()
