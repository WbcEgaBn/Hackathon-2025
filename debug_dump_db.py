from db.database import SessionLocal
from db.models import Item

db = SessionLocal()

items = db.query(Item).all()

print("\n=== DATABASE ITEM DUMP ===")

for it in items:
    print(f"\nItem ID: {it.item_id}")
    print(f"Title: {it.item_title}")
    print(f"Case Code: {it.case_code}")
    print(f"Description: {it.description}")
    print(f"Topics Detected: {it.topics_detected}")
    print(f"Location: {it.location}")
    print(f"Raw Block:\n{it.raw_block}")
    print("-" * 40)

db.close()
