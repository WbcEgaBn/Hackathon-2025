from datetime import date
from .ingestion import fetch_new_meetings
from .pdf_parser import extract_text_from_pdf
from .item_parser import parse_items
from .topic_classifier import classify_topics
from notifications.geocoder import geocode   # cached geocoder


def run_processing_pipeline(db):
    """
    Full ingestion + extraction + classification + multi-location geocoding.
    """

    new_meetings = fetch_new_meetings()
    results = []

    for meeting in new_meetings:

        # 1. Extract text --------------------------------------------------
        raw_text = extract_text_from_pdf(meeting["pdf_path"])

        # 2. Parse structured items ----------------------------------------
        parsed_items = parse_items(raw_text)

        processed_items = []

        for item in parsed_items:

            # 3. Topic classification
            topics = classify_topics(item)

            # 4. Multi-location geocoding ----------------------------------
            all_locations = item.get("all_locations", [])
            geocoded_list = []

            for loc in all_locations:
                geo = geocode(db, loc)  # cached geocoder
                if geo:
                    geocoded_list.append({
                        "address": loc,
                        "lat": geo["lat"],
                        "lon": geo["lon"]
                    })

            # 5. Construct item record --------------------------------------
            processed_item = {
                "section_code": item.get("section_code"),
                "section_title": item.get("section_title"),

                "item_title": item.get("item_title"),
                "case_code": item.get("case_code"),

                # Core extracted fields
                "description": item.get("description"),
                "location": item.get("location"),  # primary location for display
                "presenters": item.get("presenters", []),
                "raw_block": item.get("raw_block", ""),

                # NLP output
                "topics_detected": topics,
                "locations_detected": geocoded_list,  # list of ALL valid coords
            }

            processed_items.append(processed_item)

        # 6. Construct meeting block ----------------------------------------
        results.append({
            "meeting_date": meeting.get("date"),
            "type": meeting.get("type"),
            "items": processed_items,
            "raw_text": raw_text,
        })

    return results
