import re
import unicodedata

# -------------------------
# CLEANING UTILITIES
# -------------------------

def clean_line(s: str) -> str:
    """Normalize, remove mid-word breaks, collapse whitespace."""
    if not s:
        return ""

    # Normalize unicode weirdness from PDFs
    s = unicodedata.normalize("NFKC", s)

    # Remove hyphenation line breaks: "marijua-\nna" → "marijuana"
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)

    # Convert all newlines and tabs to spaces
    s = s.replace("\n", " ").replace("\t", " ")

    # Collapse repeated whitespace
    s = re.sub(r"\s+", " ", s)

    return s.strip()


def clean_block(lines):
    """Join many PDF-cut lines into one stable paragraph."""
    joined = " ".join(clean_line(l) for l in lines)
    return clean_line(joined)


# -------------------------
# REGEX DEFINITIONS
# -------------------------

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


# -------------------------
# MAIN PARSER
# -------------------------

def parse_items(text: str):
    lines = text.split("\n")

    current_section = None
    current_item = None
    items = []
    buffer = []

    for raw in lines:
        stripped = clean_line(raw)

        # --------------------------
        # SECTION HEADER (e.g., "5. Consent Calendar")
        # --------------------------
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

        # --------------------------
        # ITEM START (e.g., "5.A. CUDP-25-0021 A Conditional Use …")
        # --------------------------
        m = ITEM_RE.match(stripped)
        if m:
            if current_item:
                finalize_item(current_item, buffer)
                items.append(current_item)
                buffer = []

            section_num = m.group(1)
            letter = m.group(2)
            main_line = m.group(3)

            # Clean the main line
            main_line = clean_line(main_line)

            # Extract case code
            case_match = CASE_RE.search(main_line)
            case_code = case_match.group(0) if case_match else None

            # Clean title (the entire main line)
            item_title = main_line

            # Description is everything except the case code
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

        # --------------------------
        # ADDITIONAL ITEM BODY TEXT
        # --------------------------
        if current_item:
            if stripped:
                buffer.append(stripped)

    # finalize last item
    if current_item:
        finalize_item(current_item, buffer)
        items.append(current_item)

    return items


# -------------------------
# FINALIZATION
# -------------------------

def finalize_item(item, buffer):
    """Extract addresses, presenters, and clean raw block."""

    raw_block = clean_block(buffer)
    item["raw_block"] = raw_block

    # ADDRESS DETECTION
    m = ADDRESS_RE.search(raw_block)
    if m:
        item["location"] = m.group(0)

    # PRESENTERS LIST
    presenters = []
    capture = False

    for line in raw_block.split(" "):  # raw_block is flattened; safe split
        if PRESENTER_START.match(line.strip()):
            capture = True
            continue

        if capture:
            if "attachment" in line.lower():
                break
            presenters.append(line.strip())

    item["presenters"] = presenters
