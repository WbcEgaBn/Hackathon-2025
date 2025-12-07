# notifications/digest_builder.py

from geopy.distance import geodesic
from db.models import Item, UserLocation


def get_items_for_user(db, user):
    """
    Returns all Item objects relevant to the user.

    An item is relevant if:
      - It matches one of the user's interested_topics
      - OR it is within radius of ANY of the user's saved locations
    """

    matched = {}

    # ----------------------------------------------------
    # 1. TOPIC MATCHING (correct + summary-independent)
    # ----------------------------------------------------
    user_topics = user.interested_topics or []

    if user_topics:
        all_items = db.query(Item).all()

        for item in all_items:
            topics = item.topics_detected or []

            # require overlap
            if any(t in topics for t in user_topics):
                matched[item.item_id] = item

    # ----------------------------------------------------
    # 2. LOCATION MATCHING (multiple saved areas)
    # ----------------------------------------------------
    if user.locations:

        geo_items = (
            db.query(Item)
              .filter(Item.locations_detected.isnot(None))
              .filter(Item.locations_detected != "[]")
              .all()
        )

        for area in user.locations:
            if area.lat is None or area.lon is None:
                continue

            user_pos = (area.lat, area.lon)
            radius = area.radius_miles

            for item in geo_items:
                entry = item.locations_detected[0]

                i_lat = entry.get("lat")
                i_lon = entry.get("lon")

                # Correct check — reject only missing values
                if i_lat is None or i_lon is None:
                    continue

                item_pos = (i_lat, i_lon)
                dist = geodesic(user_pos, item_pos).miles

                if dist <= radius:
                    matched[item.item_id] = item

    # ----------------------------------------------------
    # 3. Return deduped list
    # ----------------------------------------------------
    return list(matched.values())
