import re
import unicodedata

def clean_line(s: str) -> str:
    if not s:
        return ""

    s = unicodedata.normalize("NFKC", s)

    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)

    s = s.replace("\n", " ").replace("\t", " ")

    s = re.sub(r"\s+", " ", s)

    return s.strip()


def clean_block(lines):
    joined = " ".join(clean_line(l) for l in lines)
    return clean_line(joined)


SECTION_RE = re.compile(r"^(\d+)\.\s+(.*)$")
ITEM_RE = re.compile(r"^(\d+)\.([A-Z])\.\s+(.*)$")
CASE_RE = re.compile(r"\b[A-Z]{3,}-\d{2}-\d{4}\b")

ADDRESS_RE = re.compile(
    r"\b\d{3,6}\s+[A-Za-z0-9\.\-'\s]+?\s("
    r"Street|St\.|Avenue|Ave\.|Road|Rd\.|Boulevard|Blvd\.?"
    r"|Drive|Dr\.|Lane|Ln\.|Way|Place|Pl\.|Court|Ct\.|Circle|Cir\.|View|Trail|Pkwy|Parkway"
    r")\b",
    re.IGNORECASE,
)

PRESENTER_START = re.compile(r"Presenter:?$", re.IGNORECASE)


def parse_items(text: str):
    lines = text.split("\n")

    current_section = None
    current_item = None
    items = []
    buffer = []

    for raw in lines:
        stripped = clean_line(raw)

        m = SECTION_RE.match(stripped)
        if m:
            if current_item:
                finalize_item(current_item, buffer)
                items.append(current_item)
                buffer = []

            current_section = {
                "section_number": m.group(1),
                "section_title": m.group(2),
            }
            continue

        m = ITEM_RE.match(stripped)
        if m:
            if current_item:
                finalize_item(current_item, buffer)
                items.append(current_item)
                buffer = []

            section_num = m.group(1)
            letter = m.group(2)
            main_line = m.group(3)

            main_line = clean_line(main_line)

            case_match = CASE_RE.search(main_line)
            case_code = case_match.group(0) if case_match else None

            item_title = main_line

            if case_code:
                description = main_line.replace(case_code, "").strip()
            else:
                description = main_line

            current_item = {
                "section_code": f"{section_num}.{letter}",
                "section_title": current_section["section_title"] if current_section else None,
                "item_title": item_title,
                "case_code": case_code,
                "description": description,
                "location": None,
                "presenters": [],
                "raw_block": "",
            }

            continue

        if current_item:
            if stripped:
                buffer.append(stripped)

    if current_item:
        finalize_item(current_item, buffer)
        items.append(current_item)

    return items

def finalize_item(item, buffer):

    raw_block = clean_block(buffer)
    item["raw_block"] = raw_block

    m = ADDRESS_RE.search(raw_block)
    if m:
        item["location"] = m.group(0)

    presenters = []
    capture = False

    for line in raw_block.split(" "): 
        if PRESENTER_START.match(line.strip()):
            capture = True
            continue

        if capture:
            if "attachment" in line.lower():
                break
            presenters.append(line.strip())

    item["presenters"] = presenters
