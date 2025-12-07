from sqlalchemy.orm import Session
from . import models


def create_meeting(db: Session, meeting_data: dict):
    meeting = models.Meeting(
        date=meeting_data["meeting_date"],
        type=meeting_data["type"],
        raw_text=meeting_data.get("raw_text"),

        url=meeting_data.get("url"),
        agenda_pdf_url=meeting_data.get("agenda_pdf_url"),
        accessible_pdf_url=meeting_data.get("accessible_pdf_url"),
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

def create_item(db: Session, meeting_id: int, item_data: dict):
    item = models.Item(
        meeting_id=meeting_id,

        section_code=item_data.get("section_code"),
        section_title=item_data.get("section_title"),

        item_title=item_data.get("item_title"),
        case_code=item_data.get("case_code"),
        description=item_data.get("description"),

        location=item_data.get("location"),
        presenters=item_data.get("presenters") or [],

        raw_block=item_data.get("raw_block"),

        topics_detected=item_data.get("topics_detected") or [],
        locations_detected=item_data.get("locations_detected") or [],
        embedding_vector=item_data.get("embedding_vector"),
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return item
