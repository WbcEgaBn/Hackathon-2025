import re


# -----------------------------
# Utility Extraction Helpers
# -----------------------------

def extract_acreage(text: str):
    """Extract acreage like '1.89 acres' or '18.11 acres'."""
    if not text:
        return None

    match = re.search(r"(\d+(\.\d+)?)\s*acres?", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_district(text: str):
    """Extract 'Council District 5', etc."""
    if not text:
        return None

    match = re.search(r"Council District\s+(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_zone_district(text: str):
    """
    Extract zoning district labels like:
    MX-M, PDZ, R-Flex, C6/P, etc.
    """
    if not text:
        return None

    match = re.search(r"\b([A-Za-z]{1,4}-?[A-Za-z]{0,4}\d{0,2}(?:/[A-Za-z0-9-]+)?)\b", text)
    return match.group(1) if match else None


def extract_action_type(text: str):
    """Identify key action types from the item description."""
    if not text:
        return None

    lowered = text.lower()

    ACTION_MAP = {
        "conditional use": "Conditional Use approval",
        "zone map amendment": "Zone Map Amendment (rezone)",
        "rezone": "Zone Map Amendment (rezone)",
        "development plan": "Development Plan review",
        "major modification": "Major Development Plan Modification",
        "minor modification": "Minor Development Plan Modification",
        "vacation": "Right-of-Way or Easement Vacation",
        "appeal": "Appeal hearing",
    }

    for key, label in ACTION_MAP.items():
        if key in lowered:
            return label

    return None


def extract_location(text: str):
    """Extract a street address ending with Blvd, Street, Ave, Rd, etc."""
    if not text:
        return None

    # Broad but effective
    match = re.search(
        r"\d{3,6}\s+[A-Za-z0-9 .'-]+\b(?:Boulevard|Blvd|Street|St|Avenue|Ave|Road|Rd|Highway|Hwy|Lane|Ln|Drive|Dr)\b",
        text,
        re.IGNORECASE
    )
    return match.group(0) if match else None


# ----------------------------------------------------
# MAIN SUMMARIZER
# ----------------------------------------------------

def summarize_item_rule_based(item: dict) -> str:
    """
    Create a clean, readable summary of an agenda item using rule-based logic.
    """
    title = item.get("item_title", "") or ""
    description = item.get("description", "") or ""
    raw = item.get("raw_block", "") or ""

    # Extract civic features
    acres = extract_acreage(raw)
    district = extract_district(raw)
    zone = extract_zone_district(raw)
    location = item.get("location") or extract_location(raw)
    action = extract_action_type(description)
    case_code = item.get("case_code")

    summary_parts = []

    # -------------------------
    # 1. Action sentence
    # -------------------------
    if action:
        summary_parts.append(f"This item requests {action.lower()}.")
    else:
        summary_parts.append(f"This item concerns: {title}.")

    # -------------------------
    # 2. High-level description
    # -------------------------
    if description:
        summary_parts.append(description.strip().rstrip("." ) + ".")

    # -------------------------
    # 3. Acreage
    # -------------------------
    if acres:
        summary_parts.append(f"It involves approximately {acres} acres.")

    # -------------------------
    # 4. Zone district
    # -------------------------
    if zone and zone.lower() not in description.lower():
        summary_parts.append(f"The site is zoned {zone}.")

    # -------------------------
    # 5. Location
    # -------------------------
    if location:
        summary_parts.append(f"The project is located at {location}.")

    # -------------------------
    # 6. Council District
    # -------------------------
    if district:
        summary_parts.append(f"It is located in Council District {district}.")

    # -------------------------
    # 7. Case Code reference
    # -------------------------
    if case_code:
        summary_parts.append(f"(Case ID: {case_code})")

    # Join with spaces
    return " ".join(summary_parts).strip()
