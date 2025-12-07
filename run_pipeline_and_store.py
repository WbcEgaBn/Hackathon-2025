from processing.pipeline import run_processing_pipeline
from db.database import SessionLocal
from db import crud


def main():
    db = SessionLocal()

    results = run_processing_pipeline(db)

    print(f"Processed {len(results)} meetings\n")

    for meeting_data in results:

        
        meeting = crud.create_meeting(db, meeting_data)

        date_str = meeting.date or "Unknown Date"
        type_str = meeting.type or "Unknown Type"

        print(f"Stored meeting {meeting.meeting_id}: {date_str} — {type_str}")

        for item_data in meeting_data["items"]:
            created_item = crud.create_item(db, meeting.meeting_id, item_data)

            section = created_item.section_code or ""
            title = created_item.item_title or "(No Title)"

            print(f"  → Item {created_item.item_id} stored: {section} {title}")

    db.close()
    print("\nAll data stored successfully!")


if __name__ == "__main__":
    main()
