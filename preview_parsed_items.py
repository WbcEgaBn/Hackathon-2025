from processing.pdf_parser import extract_text_from_pdf
from processing.item_parser import parse_items

pdf = "sample_data/agenda1.pdf"
text = extract_text_from_pdf(pdf)
items = parse_items(text)

print(f"Detected {len(items)} items:\n")

for i, item in enumerate(items, 1):
    print(f"--- Item {i} ---")

    # Section header like "5.A Consent Calendar"
    section_str = f"{item['section_code']} {item['section_title']}" if item['section_title'] else item['section_code']
    print("Section:", section_str)

    print("Title:", item.get("item_title"))

    if item.get("case_code"):
        print("Case Code:", item["case_code"])

    if item.get("location"):
        print("Location Affected:", item["location"])

    print("Description:", item["description"])

    # Presenters list
    if item.get("presenters"):
        print("Presenters:")
        for p in item["presenters"]:
            print("  -", p)

    print("\n")
