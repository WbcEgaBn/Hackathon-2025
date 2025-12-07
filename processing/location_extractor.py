# app/processing/location_extractor.py

import re

STREET_NAMES = [
    "academy", "powers", "tejon", "union", "platte",
    "constitution", "fillmore", "briargate",
]

AREAS = [
    "downtown", "old colorado city", "briargate",
    "northgate", "broadmoor"
]

def extract_locations(text: str):
    text_low = text.lower()
    found = []

    # Match areas
    for a in AREAS:
        if a in text_low:
            found.append(a)

    # Match street names
    for street in STREET_NAMES:
        if street in text_low:
            found.append(street)

    # Match ZIP codes
    zips = re.findall(r"\b80[0-9]{3}\b", text_low)
    found.extend(zips)

    return list(set(found))
