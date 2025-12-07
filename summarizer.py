# generate_summaries.py

from db.database import SessionLocal
from db import models
from processing.rule_summarizer import summarize_item_rule_based


def main():
    db = SessionLocal()

    print("🔍 Fetching items without summaries...")
    items = db.query(models.Item).all()

    print(f"Found {len(items)} total items.")

    updated = 0

    for item in items:
        # If summary exists, skip
        if item.processed_summary and item.processed_summary.strip():
            continue

        # Build rule-based summary
        summary = summarize_item_rule_based({
            "item_title": item.item_title,
            "description": item.description,
            "location": item.location,
            "case_code": item.case_code,
            "raw_block": item.raw_block
        })

        # Save summary
        item.processed_summary = summary
        updated += 1

    db.commit()
    db.close()

    print(f"✨ Finished! Generated {updated} new summaries.")


if __name__ == "__main__":
    main()
