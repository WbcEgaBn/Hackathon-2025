import sqlite3
from pathlib import Path
import json

DB_PATH = "meetings.db"


def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    if not Path(DB_PATH).exists():
        print(f"❌ Database '{DB_PATH}' not found!")
        print("Run init_db.py or the data pipeline first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print_section("TABLES IN DATABASE")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]

    for t in tables:
        print(f"- {t}")

    if "meetings" in tables:
        print_section("MEETINGS TABLE")

        cursor.execute("""
            SELECT meeting_id, date, type, url 
            FROM meetings 
            ORDER BY meeting_id DESC;
        """)

        for r in cursor.fetchall():
            print(f"ID: {r[0]} | Date: {r[1]} | Type: {r[2]} | URL: {r[3]}")

    if "items" in tables:
        print_section("ITEMS TABLE (Showing First 10)")

        cursor.execute("""
            SELECT 
                item_id, meeting_id, section_code, item_title, 
                case_code, location
            FROM items
            ORDER BY item_id
            LIMIT 10;
        """)

        rows = cursor.fetchall()

        for r in rows:
            print(
                f"ItemID: {r[0]} | MeetingID: {r[1]} "
                f"| Section: {r[2]} | Title: {r[3]} "
                f"| Case: {r[4]} | Location: {r[5]}"
            )

    if "items" in tables:
        print_section("TOPICS DETECTED FOR ITEMS")

        cursor.execute("""
            SELECT item_id, item_title, topics_detected
            FROM items
            ORDER BY item_id
            LIMIT 10;
        """)

        rows = cursor.fetchall()

        for item_id, title, topics in rows:
            topics_display = topics if topics else "[]"
            print(f"ItemID: {item_id} | {title}")
            print(f" → Topics: {topics_display}\n")

    if "items" in tables:
        print_section("AI-GENERATED SUMMARIES")

        cursor.execute("""
            SELECT item_id, item_title, processed_summary
            FROM items
            ORDER BY item_id
            LIMIT 10;
        """)

        rows = cursor.fetchall()

        for item_id, title, summary in rows:
            summary = summary or "(No summary generated)"
            print(f"ItemID: {item_id} | Title: {title}")
            print(f"Summary:\n{summary}\n")

    if "users" in tables:
        print_section("USERS & THEIR INTERESTS")

        cursor.execute("""
            SELECT user_id, email, interested_topics
            FROM users
            ORDER BY user_id;
        """)

        users = cursor.fetchall()

        for user_id, email, raw_topics in users:
            try:
                topics = json.loads(raw_topics) if raw_topics else []
            except:
                topics = raw_topics  # fallback

            print(f"UserID: {user_id} | Email: {email}")
            print(f" → Topics: {topics}")

            # Fetch locations for each user
            print("   Locations:")

            cursor.execute("""
                SELECT id, label, address, normalized_address,
                       lat, lon, radius_miles
                FROM user_locations
                WHERE user_id = ?
            """, (user_id,))

            locs = cursor.fetchall()

            if locs:
                for loc in locs:
                    print(
                        f"     - {loc[1]} | {loc[2]} "
                        f"(radius: {loc[6]} mi, lat/lon: {loc[4]}, {loc[5]})"
                    )
            else:
                print("     (None)")

            print()

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
