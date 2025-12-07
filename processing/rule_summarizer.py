import re


def extract_acreage(text: str):
    if not text:
        return None

    match = re.search(r"(\d+(\.\d+)?)\s*acres?", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_district(text: str):
    if not text:
        return None

    match = re.search(r"Council District\s+(\d+)", text, re.IGNORECASE)
    return match.group(1) if match else None


def extract_zone_district(text: str):
    if not text:
        return None

    match = re.search(r"\b([A-Za-z]{1,4}-?[A-Za-z]{0,4}\d{0,2}(?:/[A-Za-z0-9-]+)?)\b", text)
    return match.group(1) if match else None


def extract_action_type(text: str):
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
    if not text:
        return None

    match = re.search(
        r"\d{3,6}\s+[A-Za-z0-9 .'-]+\b(?:Boulevard|Blvd|Street|St|Avenue|Ave|Road|Rd|Highway|Hwy|Lane|Ln|Drive|Dr)\b",
        text,
        re.IGNORECASE
    )
    return match.group(0) if match else None

def summarize_item_rule_based(item: dict) -> str:
    title = item.get("item_title", "") or ""
    description = item.get("description", "") or ""
    raw = item.get("raw_block", "") or ""

    acres = extract_acreage(raw)
    district = extract_district(raw)
    zone = extract_zone_district(raw)
    location = item.get("location") or extract_location(raw)
    action = extract_action_type(description)
    case_code = item.get("case_code")

    summary_parts = []

    if action:
        summary_parts.append(f"This item requests {action.lower()}.")
    else:
        summary_parts.append(f"This item concerns: {title}.")

    if description:
        summary_parts.append(description.strip().rstrip("." ) + ".")

    if acres:
        summary_parts.append(f"It involves approximately {acres} acres.")

    if zone and zone.lower() not in description.lower():
        summary_parts.append(f"The site is zoned {zone}.")
        
    if location:
        summary_parts.append(f"The project is located at {location}.")

    if district:
        summary_parts.append(f"It is located in Council District {district}.")

    if case_code:
        summary_parts.append(f"(Case ID: {case_code})")

    return " ".join(summary_parts).strip()
