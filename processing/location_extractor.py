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

    for a in AREAS:
        if a in text_low:
            found.append(a)

    for street in STREET_NAMES:
        if street in text_low:
            found.append(street)

    zips = re.findall(r"\b80[0-9]{3}\b", text_low)
    found.extend(zips)

    return list(set(found))
